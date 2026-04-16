"""基金API路由"""
from flask import Blueprint, jsonify, request
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.eastmoney import EastmoneyService

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