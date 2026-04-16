"""MiniMax AI 文案生成服务"""
import requests
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import Config

MINIMAX_TOKEN = Config.MINIMAX_TOKEN
MINIMAX_API = Config.MINIMAX_API

TEMPLATES = {
    "朋友圈文案": """📈 {name}

各位朋友好！给大家推荐一只我很看好的基金——{name}！

近一年收益达到 {y1}，大幅跑赢同类平均水平！

✅ {points}

{company}出品，{manager}掌舵，值得信赖！

💬 感兴趣的朋友可以私信我了解详情~

⚠️ 基金有风险，投资需谨慎""",
    "一句话推荐": """🌟 {name} | {company} | {y1}年化收益""",
    "微信群发": """【基金推荐】
{name}
代码：{code}
类型：{type}

📈 近一年收益：{y1}
🏆 同类排名：{rank}
👨‍💼 基金经理：{manager}

有意向的朋友欢迎咨询！

风险提示：基金有风险，投资需谨慎""",
    "微信图文": """# {name}

## 基金概况
- 代码：{code}
- 类型：{type}
- 公司：{company}
- 经理：{manager}

## 业绩表现
- 近一年：{y1}
- 近三年：{y3}
- 排名：{rank}

## 推荐理由
1. {points}
2. {company}旗下产品
3. {manager}管理

## 风险提示
基金有风险，投资需谨慎"""
}

class MiniMaxService:
    """MiniMax AI 文案生成"""
    
    @classmethod
    def generate_copy(cls, fund_info, selling_points, format_type="朋友圈文案", style="亲切易懂"):
        """生成营销文案"""
        template = TEMPLATES.get(format_type, TEMPLATES["朋友圈文案"])
        
        if selling_points:
            if isinstance(selling_points[0], dict):
                points = "、".join([sp.get('title', '') for sp in selling_points[:3]])
            else:
                points = "、".join(selling_points[:3])
        else:
            points = "长期表现稳健"
        
        # 语气调整
        if style == "专业正式":
            template = template.replace("各位朋友好", "尊敬的投资者")
            template = template.replace("感兴趣的朋友", "有投资意向的客户")
        
        content = template.format(
            name=fund_info.get('name', '优质基金'),
            code=fund_info.get('code', ''),
            type=fund_info.get('type', '混合型'),
            company=fund_info.get('company', ''),
            manager=fund_info.get('manager', '专业经理'),
            y1=fund_info.get('y1', '+0%'),
            y3=fund_info.get('y3', '+0%'),
            rank=fund_info.get('rank', '前50%'),
            points=points
        )
        
        return content
    
    @classmethod
    def generate_with_ai(cls, fund_info, selling_points, format_type, style):
        """调用MiniMax API生成"""
        prompt = f"""请为基金"{fund_info.get('name', '')}"生成一段{format_type}风格的营销文案。

基金信息：
- 代码：{fund_info.get('code', '')}
- 公司：{fund_info.get('company', '')}
- 经理：{fund_info.get('manager', '')}
- 近一年收益：{fund_info.get('y1', '')}
- 风格：{style}

卖点：
"""
        for sp in (selling_points or []):
            if isinstance(sp, dict):
                prompt += f"- {sp.get('title', '')}: {sp.get('desc', '')}\n"
            else:
                prompt += f"- {sp}\n"
        
        prompt += """
要求：专业但不生硬，突出业绩，提醒风险，字数适中。直接输出文案，不要markdown格式。"""
        
        try:
            headers = {"Authorization": f"Bearer {MINIMAX_TOKEN}", "Content-Type": "application/json"}
            data = {"model": "abab6.5s-chat", "tokens_to_generate": 512, "messages": [
                {"role": "system", "content": "你是基金营销文案专家。"},
                {"role": "user", "content": prompt}
            ]}
            
            resp = requests.post(MINIMAX_API, headers=headers, json=data, timeout=30)
            if resp.status_code == 200:
                result = resp.json()
                content = result.get("choices", [{}])[0].get("messages", [{}])[0].get("content", "")
                if content:
                    return content.strip()
        except Exception as e:
            print(f"MiniMax API失败: {e}")
        
        return cls.generate_copy(fund_info, selling_points, format_type, style)
