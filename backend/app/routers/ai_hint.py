import httpx
import json
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AIHintRecord, Question, SystemConfig, HintLevel, User
from app.schemas.ai import AIHintRequest, AIHintResponse
from app.dependencies import get_current_user
from app.config import settings

router = APIRouter(prefix="/api/ai-hint", tags=["AI提示"])

# AI Provider configurations
AI_PROVIDERS = {
    "openai": {
        "name": "OpenAI (GPT)",
        "default_url": "https://api.openai.com/v1/chat/completions",
        "default_model": "gpt-3.5-turbo",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
    },
    "deepseek": {
        "name": "DeepSeek",
        "default_url": "https://api.deepseek.com/v1/chat/completions",
        "default_model": "deepseek-chat",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
    },
    "zhipu": {
        "name": "智谱AI (GLM)",
        "default_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "default_model": "glm-4-flash",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
    },
    "qwen": {
        "name": "阿里通义千问",
        "default_url": "https://dashscope.aliyuncs.com/api/v1/chat/completions",
        "default_model": "qwen-turbo",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
    },
    "google": {
        "name": "Google Gemini",
        "default_url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
        "default_model": "gemini-pro",
        "auth_header": "x-goog-api-key",
        "auth_prefix": "",
    },
    "moonshot": {
        "name": "Moonshot (Kimi)",
        "default_url": "https://api.moonshot.cn/v1/chat/completions",
        "default_model": "moonshot-v1-8k",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
    },
    "pangu": {
        "name": "华为云盘古",
        "default_url": "https://pangu-api.cn-north-4.myhuaweicloud.com/v1/chat/completions",
        "default_model": "pangu-n2",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
    },
    "wenxin": {
        "name": "百度文心",
        "default_url": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxin/chat/completions",
        "default_model": "ernie-bot-turbo",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
    },
    "custom": {
        "name": "自定义API",
        "default_url": "",
        "default_model": "",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
    },
}


def get_ai_config(db: Session) -> dict:
    """从数据库获取AI配置"""
    configs = db.query(SystemConfig).filter(SystemConfig.key.like("ai_%")).all()
    config = {c.key.replace("ai_", ""): c.value for c in configs}
    return {
        "provider": config.get("provider") or "openai",
        "api_url": config.get("api_url") or "",
        "api_key": config.get("api_key") or "",
        "model_name": config.get("model_name") or "gpt-3.5-turbo",
        "prompt_template": config.get("prompt_template") or DEFAULT_PROMPT_TEMPLATE,
        "daily_limit": int(config.get("daily_limit") or 50),
        "enabled": config.get("enabled") == "true",
    }


DEFAULT_PROMPT_TEMPLATE = """你是一个专业的密码学考试辅导老师。请根据以下题目给出提示和解析。

【题目】
{question}

【选项】
{options}

【要求】
- 提示级别：{level}
- 请根据提示级别给出相应深度的指导
- 轻度提示：只给出知识点提示和思考方向
- 中度提示：给出解题思路和关键步骤
- 深度提示：详细解析题目，说明每个选项的对错原因
- 注意：不要直接给出答案，要引导学生思考
- 用中文回答，语言简洁专业"""


@router.post("/request")
def request_hint(data: AIHintRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == data.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    # Get AI config
    ai_config = get_ai_config(db)
    
    # Check daily limit
    today = date.today()
    used_today = db.query(AIHintRecord).filter(
        AIHintRecord.user_id == current_user.id,
        AIHintRecord.created_at >= datetime.combine(today, datetime.min.time()),
    ).count()
    
    daily_limit = ai_config.get("daily_limit", 50)
    if used_today >= daily_limit:
        raise HTTPException(status_code=429, detail=f"今日AI提示次数已用完（{daily_limit}次/天）")
    
    # Check per-question limit
    used_for_question = db.query(AIHintRecord).filter(
        AIHintRecord.user_id == current_user.id,
        AIHintRecord.question_id == data.question_id,
    ).count()
    
    if used_for_question >= 3:
        raise HTTPException(status_code=429, detail="本题提示次数已达上限（3次）")
    
    # Generate hint
    if not ai_config.get("enabled") or not ai_config.get("api_key"):
        hint_content = _generate_fallback_hint(question, data.level)
    else:
        try:
            hint_content = _generate_ai_hint(question, data.level, ai_config, db)
        except Exception as e:
            print(f"AI API error: {e}")
            hint_content = _generate_fallback_hint(question, data.level)
    
    # Record
    record = AIHintRecord(
        user_id=current_user.id,
        question_id=data.question_id,
        hint_level=data.level,
        hint_content=hint_content,
    )
    db.add(record)
    db.commit()
    
    remaining_today = daily_limit - used_today - 1
    remaining_question = 3 - used_for_question - 1
    
    return AIHintResponse(
        hint_content=hint_content,
        hint_level=data.level,
        remaining_count=remaining_question,
    )


@router.post("/chat")
def ai_chat(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """AI多轮对话接口"""
    question_id = data.get("question_id")
    messages = data.get("messages", [])
    
    if not messages:
        raise HTTPException(status_code=400, detail="消息不能为空")
    
    # Get question if provided
    question = None
    if question_id:
        question = db.query(Question).filter(Question.id == question_id).first()
    
    # Get AI config
    ai_config = get_ai_config(db)
    
    if not ai_config.get("enabled") or not ai_config.get("api_key"):
        return {"content": "AI服务未启用，请联系管理员配置API Key。"}
    
    # Check daily limit
    today = date.today()
    used_today = db.query(AIHintRecord).filter(
        AIHintRecord.user_id == current_user.id,
        AIHintRecord.created_at >= datetime.combine(today, datetime.min.time()),
    ).count()
    
    daily_limit = ai_config.get("daily_limit", 50)
    if used_today >= daily_limit:
        raise HTTPException(status_code=429, detail=f"今日AI对话次数已用完（{daily_limit}次/天）")
    
    try:
        response = _call_ai_chat(messages, ai_config, question)
        
        # Record usage
        record = AIHintRecord(
            user_id=current_user.id,
            question_id=question_id,
            hint_level=HintLevel.deep,
            hint_content=messages[-1].get("content", "")[:200],
        )
        db.add(record)
        db.commit()
        
        return {"content": response}
    except Exception as e:
        print(f"AI chat error: {e}")
        return {"content": f"AI服务暂时不可用：{str(e)}"}


@router.get("/usage")
def get_usage(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    today = date.today()
    used_today = db.query(AIHintRecord).filter(
        AIHintRecord.user_id == current_user.id,
        AIHintRecord.created_at >= datetime.combine(today, datetime.min.time()),
    ).count()
    ai_config = get_ai_config(db)
    daily_limit = ai_config.get("daily_limit", 50)
    return {
        "total_hints_used": used_today,
        "daily_limit": daily_limit,
        "remaining_today": daily_limit - used_today,
    }


@router.get("/remaining/{question_id}")
def get_remaining(question_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    used = db.query(AIHintRecord).filter(
        AIHintRecord.user_id == current_user.id,
        AIHintRecord.question_id == question_id,
    ).count()
    return {"remaining": max(0, 3 - used)}


@router.get("/providers")
def get_providers():
    """获取支持的AI服务商列表"""
    return {
        "providers": [
            {"key": k, "name": v["name"], "default_url": v["default_url"], "default_model": v["default_model"]}
            for k, v in AI_PROVIDERS.items()
        ]
    }


def _generate_fallback_hint(question: Question, level: HintLevel) -> str:
    kp = question.knowledge_point or "密码学"
    qt_map = {"single": "单选题", "multi": "多选题", "judge": "判断题"}
    qt = qt_map.get(question.question_type.value, "题目")
    
    if level == HintLevel.light:
        return f"💡 **知识点提示**\n\n这道{qt}涉及「**{kp}**」相关内容。\n\n建议：\n- 回顾该知识点的核心概念和基本原理\n- 注意题目中的关键词和限定条件\n- 排除明显不合理的选项"
    elif level == HintLevel.medium:
        return f"💡 **解题思路**\n\n这道{qt}涉及「**{kp}**」。\n\n解题步骤：\n1. 仔细审题，找出题目考查的核心概念\n2. 分析每个选项，判断其是否符合定义或原理\n3. 对于错误选项，思考其错误原因\n4. 选择最符合题意的答案\n\n注意：题目中可能存在陷阱，要仔细辨析概念间的细微差别。"
    else:
        return f"💡 **深度解析**\n\n这道{qt}涉及「**{kp}**」。\n\n**知识点回顾：**\n{kp}是密码学中的重要概念，需要理解其定义、特点和应用场景。\n\n**解题方法：**\n1. 从基本定义出发，明确概念内涵\n2. 分析各选项与定义的对应关系\n3. 注意区分相似概念的差异\n4. 结合实际应用场景验证答案\n\n**常见误区：**\n- 混淆相关概念\n- 忽略限定条件\n- 过度推断或理解偏差"


def _generate_ai_hint(question: Question, level: HintLevel, config: dict, db: Session) -> str:
    """调用AI API生成提示"""
    provider = config.get("provider", "openai")
    provider_config = AI_PROVIDERS.get(provider, AI_PROVIDERS["openai"])
    
    api_url = config.get("api_url") or provider_config["default_url"]
    api_key = config.get("api_key")
    model = config.get("model_name") or provider_config["default_model"]
    prompt_template = config.get("prompt_template") or DEFAULT_PROMPT_TEMPLATE
    
    # Build options text
    options_text = ""
    if question.options:
        for opt in sorted(question.options, key=lambda x: x.sort_order):
            options_text += f"{opt.label}. {opt.content}\n"
    
    level_map = {"light": "轻度", "medium": "中度", "deep": "深度"}
    level_text = level_map.get(level.value, "中度")
    
    prompt = prompt_template.format(
        question=question.content,
        options=options_text or "（判断题）",
        level=level_text,
    )
    
    messages = [{"role": "user", "content": prompt}]
    
    return _call_ai_chat(messages, config, question)


def _call_ai_chat(messages: list, config: dict, question: Question = None) -> str:
    """调用AI聊天API"""
    provider = config.get("provider", "openai")
    provider_config = AI_PROVIDERS.get(provider, AI_PROVIDERS["openai"])
    
    api_url = config.get("api_url") or provider_config["default_url"]
    api_key = config.get("api_key")
    model = config.get("model_name") or provider_config["default_model"]
    
    if not api_url or not api_key:
        raise ValueError("API URL或API Key未配置")
    
    # Build request based on provider
    if provider == "google":
        # Google Gemini format
        headers = {
            "Content-Type": "application/json",
            provider_config["auth_header"]: api_key,
        }
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        payload = {"contents": contents}
    else:
        # OpenAI-compatible format (OpenAI, DeepSeek, Zhipu, Qwen, Moonshot, etc.)
        headers = {
            "Content-Type": "application/json",
            provider_config["auth_header"]: provider_config["auth_prefix"] + api_key,
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024,
        }
    
    # Make request
    with httpx.Client(timeout=30.0) as client:
        response = client.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
    
    # Parse response based on provider
    if provider == "google":
        return result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    else:
        return result.get("choices", [{}])[0].get("message", {}).get("content", "")
