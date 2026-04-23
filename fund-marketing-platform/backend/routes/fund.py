"""基金API路由"""
from flask import Blueprint, jsonify, request
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.eastmoney import EastmoneyService
from services.tiantianfund import TiantianFundService

fund_bp = Blueprint('fund', __name__)

@fund_bp.route('/list')
def list_funds():
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        keyword = request.args.get('keyword', '') or request.args.get('q', '')
        
        if keyword:
            funds = EastmoneyService.search_funds(keyword, 100)
        else:
            funds = EastmoneyService.get_fund_list()
        
        total = len(funds)
        start = (page - 1) * page_size
        end = start + page_size
        items = funds[start:end]
        
        return jsonify({'success': True, 'data': items, 'total': total, 'page': page, 'page_size': page_size})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fund_bp.route('/search')
def search():
    try:
        keyword = request.args.get('q', '') or request.args.get('keyword', '')
        limit = request.args.get('limit', 20, type=int)
        
        # First search in fund list
        results = EastmoneyService.search_funds(keyword, limit)
        
        # If no results and keyword looks like a fund code (6 digits), try to get details directly
        if not results and keyword.isdigit() and len(keyword) >= 5:
            detail = EastmoneyService.get_fund_detail(keyword)
            if detail:
                results = [detail]
        
        # If still no results, try searching with different query
        if not results and len(keyword) >= 2:
            # Try partial match
            all_funds = EastmoneyService.get_fund_list()
            keyword_lower = keyword.lower()
            results = [f for f in all_funds if keyword_lower in f['code'].lower() or keyword_lower in f['name'].lower()][:limit]
        
        return jsonify({'success': True, 'data': results, 'count': len(results)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fund_bp.route('/<code>')
def detail(code):
    try:
        detail = EastmoneyService.get_fund_detail(code)
        if detail:
            return jsonify({'success': True, 'data': detail})
        
        funds = EastmoneyService.get_fund_list()
        fund = next((f for f in funds if f['code'] == code), None)
        if fund:
            return jsonify({'success': True, 'data': fund})
        return jsonify({'success': False, 'error': '基金不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fund_bp.route('/<code>/detail')
def fund_detail(code):
    try:
        detail = EastmoneyService.get_fund_detail(code)
        if detail:
            return jsonify({'success': True, 'data': detail})
        return jsonify({'success': False, 'error': '获取基金详情失败'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fund_bp.route('/<code>/full')
def fund_full(code):
    try:
        detail = EastmoneyService.get_fund_detail(code)
        history = EastmoneyService.get_fund_nav_history(code, 365)
        hotspots = EastmoneyService.get_hotspots(code)
        
        if not detail:
            return jsonify({'success': False, 'error': '获取基金详情失败'}), 404
        
        return jsonify({
            'success': True,
            'data': {
                'detail': detail,
                'history': history,
                'hotspots': hotspots
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fund_bp.route('/<code>/hotspots')
def fund_hotspots(code):
    try:
        hotspots = EastmoneyService.get_hotspots(code)
        return jsonify({'success': True, 'data': hotspots})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fund_bp.route('/<code>/nav')
def fund_nav(code):
    try:
        days = request.args.get('days', 180, type=int)
        history = EastmoneyService.get_fund_nav_history(code, days)
        return jsonify({'success': True, 'data': history})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fund_bp.route('/home/recommend')
def home_recommend():
    try:
        codes = ['163406', '003095', '161005', '110022', '161725', '320007', '000198', '004512']
        funds = []
        for code in codes:
            detail = EastmoneyService.get_fund_detail(code)
            if detail:
                funds.append(detail)
            else:
                funds.append({'code': code, 'name': '加载中...'})
        return jsonify({'success': True, 'data': funds})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fund_bp.route('/<code>/rank')
def fund_rank(code):
    try:
        rank_data = TiantianFundService.get_fund_rank(code)
        if rank_data:
            return jsonify({'success': True, 'data': rank_data})
        return jsonify({'success': False, 'error': '获取排名数据失败'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fund_bp.route('/<code>/comparison')
def fund_comparison(code):
    try:
        comparison_data = TiantianFundService.get_performance_comparison(code)
        if comparison_data:
            return jsonify({'success': True, 'data': comparison_data})
        return jsonify({'success': False, 'error': '获取对比数据失败'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fund_bp.route('/<code>/full_plus')
def fund_full_plus(code):
    try:
        detail = EastmoneyService.get_fund_detail(code)
        history = EastmoneyService.get_fund_nav_history(code, 365)
        hotspots = EastmoneyService.get_hotspots(code)
        rank_data = TiantianFundService.get_fund_rank(code)
        comparison_data = TiantianFundService.get_performance_comparison(code)
        
        if not detail:
            return jsonify({'success': False, 'error': '获取基金详情失败'}), 404
        
        return jsonify({
            'success': True,
            'data': {
                'detail': detail,
                'history': history,
                'hotspots': hotspots,
                'rank': rank_data,
                'comparison': comparison_data
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fund_bp.route('/copywriting', methods=['POST'])
def generate_copywriting():
    try:
        data = request.json
        fund_info = data.get('fund_info', {})
        selling_points = data.get('selling_points', [])
        format_type = data.get('format_type', '朋友圈短文')
        style = data.get('style', '亲切易懂')
        
        # 构建提示词
        prompt = f"""请为基金产品生成一篇营销文案。

基金信息：
- 基金名称：{fund_info.get('name', '海富通沪深300指数增强C')}
- 基金代码：{fund_info.get('code', '004512')}
- 基金类型：{fund_info.get('type', '混合型')}
- 近1年收益：{fund_info.get('y1', fund_info.get('yield_1y', '—'))}
- 近3年收益：{fund_info.get('y3', fund_info.get('yield_3y', '—'))}
- 夏普比率：{fund_info.get('sharpe', '—')}
- 最大回撤：{fund_info.get('dd', fund_info.get('drawdown', '—'))}
- 基金经理：{fund_info.get('manager', '—')}
- 基金公司：{fund_info.get('company', '—')}

选定卖点：
{chr(10).join([f"- {point}" for point in selling_points])}

文案要求：
- 格式：{format_type}
- 风格：{style}
- 字数：根据格式要求适当调整
- 内容：结合基金信息和选定卖点，突出产品优势
- 语言：简洁明了，富有感染力
- 结尾：包含风险提示
"""
        
        # 模拟AI生成文案
        # 实际项目中可以调用真实的AI API
        # 使用\n作为换行符，确保在前端正确显示
        generated_content = f"{fund_info.get('name', '海富通沪深300指数增强C')}，您的投资新选择！\n\n"
        generated_content += "\n".join([f"• {point}" for point in selling_points])
        generated_content += f"\n\n该基金由{fund_info.get('manager', '专业基金经理')}精心管理，"
        generated_content += f"近1年收益{fund_info.get('y1', fund_info.get('yield_1y', '—'))}，表现出色。\n\n"
        generated_content += f"选择{fund_info.get('name', '海富通沪深300指数增强C')}，把握市场机遇，开启您的财富增长之旅！\n\n"
        generated_content += "*基金有风险，投资需谨慎。过往业绩不代表未来表现。*"
        
        return jsonify({
            'success': True,
            'data': {
                'content': generated_content
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500