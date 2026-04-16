"""东方财富数据服务 + akshare备用"""
import requests
import json
import re
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import Config

class EastmoneyService:
    """东方财富数据获取 (主数据源)"""
    
    FUND_LIST_URL = "https://fund.eastmoney.com/js/fundcode_search.js"
    PINGZHONG_BASE = "https://fund.eastmoney.com/pingzhongdata"
    SEARCH_URL = "https://fund.eastmoney.com/center/gridlist.html"
    
    _cache = {}
    _cache_time = {}
    CACHE_DURATION = Config.CACHE_DURATION
    
    @classmethod
    def get_fund_list(cls):
        if 'fund_list' in cls._cache:
            if datetime.now().timestamp() - cls._cache_time.get('fund_list', 0) < cls.CACHE_DURATION:
                return cls._cache['fund_list']
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Referer': 'https://fund.eastmoney.com/'
            }
            resp = requests.get(cls.FUND_LIST_URL, headers=headers, timeout=10)
            match = re.search(r'\[.*\]', resp.text, re.DOTALL)
            if match:
                funds = json.loads(match.group())
                result = [{'code': f[0], 'name': f[2], 'type': cls.normalize_type(f[3]), 'company': f[4]} for f in funds[:500]]
                cls._cache['fund_list'] = result
                cls._cache_time['fund_list'] = datetime.now().timestamp()
                return result
        except Exception as e:
            print(f"获取基金列表失败: {e}")
        return cls.get_backup_funds()
    
    @classmethod
    def get_fund_detail(cls, code):
        cache_key = f'detail_{code}'
        if cache_key in cls._cache:
            if datetime.now().timestamp() - cls._cache_time.get(cache_key, 0) < cls.CACHE_DURATION:
                return cls._cache[cache_key]
        
        try:
            url = f"{cls.PINGZHONG_BASE}/{code}.js"
            headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://fund.eastmoney.com/'}
            resp = requests.get(url, headers=headers, timeout=10)
            text = resp.text
            
            data = {}
            
            name_match = re.search(r'var fS_name\s*=\s*"([^"]+)"', text)
            if name_match:
                data['name'] = name_match.group(1)
            
            code_match = re.search(r'var fS_code\s*=\s*"([^"]+)"', text)
            if code_match:
                data['code'] = code_match.group(1)
            
            manager_arr_match = re.search(r'var Data_currentFundManager\s*=\s*(\[.*?\]);', text)
            if manager_arr_match:
                try:
                    managers = eval(manager_arr_match.group(1))
                    if managers and len(managers) > 0:
                        data['manager'] = managers[0].get('name', '')
                        data['manager_start'] = managers[0].get('startDate', '')
                except:
                    pass
            
            company_match = re.search(r'var Data_company\s*=\s*(\{[^}]+\});', text)
            if company_match:
                try:
                    company_data = json.loads(company_match.group(1))
                    data['company'] = company_data.get('shortName', company_data.get('name', ''))
                except:
                    pass
            
            yield_1n_match = re.search(r'var Data_rateInSimilarPersent\s*=\s*(\{[^}]+\});', text)
            if yield_1n_match:
                try:
                    perf_data = json.loads(yield_1n_match.group(1))
                    data['yield_1y'] = perf_data.get('sy', perf_data.get('syl_1n', ''))
                    data['yield_3y'] = perf_data.get('syl_3n', '')
                    data['yield_6m'] = perf_data.get('syl_6y', '')
                    data['rank_1y'] = perf_data.get('syl_1n_pct', '')
                    data['rank_3y'] = perf_data.get('syl_3n_pct', '')
                except:
                    pass
            
            net_worth_match = re.search(r'var Data_netWorthTrend\s*=\s*(\[.*?\]);', text)
            nav_match = re.search(r'var Data_grandTotal\s*=\s*(\[.*?\]);', text)
            
            if net_worth_match:
                try:
                    nav_data = eval(net_worth_match.group(1))
                    if nav_data and len(nav_data) > 0:
                        last_nav = nav_data[-1]
                        data['nav'] = last_nav.get('y', '')
                        data['nav_date'] = datetime.fromtimestamp(last_nav.get('x', 0)/1000).strftime('%Y-%m-%d') if last_nav.get('x') else ''
                except:
                    pass
            
            if data.get('name'):
                # Extract yield data from simple variables
                y1_match = re.search(r'var syl_1n\s*=\s*"([^"]+)"', text)
                y3_match = re.search(r'var syl_3n\s*=\s*"([^"]+)"', text)
                y6_match = re.search(r'var syl_6y\s*=\s*"([^"]+)"', text)
                y3m_match = re.search(r'var syl_3y\s*=\s*"([^"]+)"', text)
                rank_match = re.search(r'var s_yl_1n_pct\s*=\s*"([^"]+)"', text)
                
                yield_1y = y1_match.group(1) if y1_match else ''
                yield_3y = y3_match.group(1) if y3_match else ''
                yield_6m = y6_match.group(1) if y6_match else ''
                yield_3m = y3m_match.group(1) if y3m_match else ''
                rank_1y = rank_match.group(1) if rank_match else ''
                
                result = {
                    'code': code, 
                    'name': data.get('name', ''), 
                    'type': '混合型',
                    'company': data.get('company', ''), 
                    'manager': data.get('manager', ''),
                    'nav': data.get('nav', ''), 
                    'nav_date': data.get('nav_date', ''),
                    'yield_1y': cls.format_yield(yield_1y),
                    'yield_3y': cls.format_yield(yield_3y),
                    'yield_6m': cls.format_yield(yield_6m), 
                    'yield_3m': cls.format_yield(yield_3m),
                    'sharpe': '', 
                    'drawdown': '',
                    'rank': rank_1y,
                }
                cls._cache[cache_key] = result
                cls._cache_time[cache_key] = datetime.now().timestamp()
                return result
        except Exception as e:
            print(f"获取基金详情失败 {code}: {e}")
        return None
    
    @classmethod
    def get_fund_nav_history(cls, code, days=180):
        cache_key = f'nav_history_{code}_{days}'
        if cache_key in cls._cache:
            return cls._cache[cache_key]
        
        try:
            url = f"https://fund.eastmoney.com/f10/F10DataApi.aspx"
            params = {
                'type': 'lsdj',
                'code': code,
                'sdate': '',
                'edate': '',
                'rt': datetime.now().timestamp()
            }
            headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://fund.eastmoney.com/'}
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            
            pattern = r'<tr><td>(\d{4}-\d{2}-\d{2})</td><td>([\d.]+)</td><td>([\d.]+)</td></tr>'
            matches = re.findall(pattern, resp.text)
            
            if matches:
                data = []
                for date, nav, acc_nav in matches[-days:]:
                    data.append({'date': date, 'nav': float(nav), 'acc_nav': float(acc_nav)})
                cls._cache[cache_key] = data
                return data
        except Exception as e:
            print(f"获取净值历史失败 {code}: {e}")
        return []
    
    @classmethod
    def get_hotspots(cls, code):
        detail = cls.get_fund_detail(code)
        if not detail:
            return []
        
        hotspots = []
        yield_1y = detail.get('yield_1y', '')
        if yield_1y and yield_1y != '+0%':
            try:
                val = float(yield_1y.replace('%', '').replace('+', ''))
                if val > 20:
                    hotspots.append({'title': '高收益基金', 'desc': f'近一年收益{yield_1y}', 'tag': '高收益', 'source': '东方财富'})
                elif val > 10:
                    hotspots.append({'title': '稳健收益', 'desc': f'近一年收益{yield_1y}', 'tag': '稳健', 'source': '东方财富'})
            except:
                pass
        
        rank = detail.get('rank', '')
        if rank:
            hotspots.append({'title': f'同类排名', 'desc': f'近一年排名{rank}', 'tag': '排名', 'source': '东方财富'})
        
        fund_type = detail.get('type', '')
        if '指数' in fund_type or 'ETF' in fund_type:
            hotspots.append({'title': '指数基金', 'desc': '被动跟踪指数', 'tag': '指数', 'source': '东方财富'})
        
        if '混合' in fund_type:
            hotspots.append({'title': '混合基金', 'desc': '灵活配置大类资产', 'tag': '混合', 'source': '东方财富'})
        
        if not hotspots:
            hotspots.append({'title': '优质基金', 'desc': '值得关注的基金', 'tag': '推荐', 'source': '东方财富'})
        
        return hotspots
    
    @classmethod
    def search_funds(cls, keyword, limit=20):
        all_funds = cls.get_fund_list()
        if not keyword:
            return all_funds[:limit]
        keyword = keyword.lower()
        results = [f for f in all_funds if keyword in f['code'].lower() or keyword in f['name'].lower()]
        return results[:limit]
    
    @classmethod
    def normalize_type(cls, t):
        if not t: return '混合型'
        t = str(t).lower()
        if '股票' in t: return '股票型'
        elif '混合' in t: return '混合型'
        elif '债券' in t: return '债券型'
        elif '货币' in t: return '货币型'
        elif '指数' in t: return '指数型'
        elif 'QDII' in t: return 'QDII'
        return '混合型'
    
    @classmethod
    def format_yield(cls, v):
        if not v: return '+0%'
        try:
            if isinstance(v, str):
                v = v.strip()
                if '%' in v:
                    return v
                v = float(v)
            return f'+{v:.2f}%' if v >= 0 else f'{v:.2f}%'
        except: return '+0%'
    
    @classmethod
    def get_backup_funds(cls):
        return [
            {"code": "163406", "name": "兴全合润混合（LOF）", "type": "混合型", "company": "兴证全球基金"},
            {"code": "003095", "name": "中欧医疗健康混合A", "type": "混合型", "company": "中欧基金"},
            {"code": "161005", "name": "富国天惠成长混合A", "type": "混合型", "company": "富国基金"},
            {"code": "110022", "name": "易方达消费行业股票", "type": "股票型", "company": "易方达基金"},
            {"code": "161725", "name": "招商中证白酒指数（LOF）", "type": "指数型", "company": "招商基金"},
            {"code": "320007", "name": "诺安成长混合", "type": "混合型", "company": "诺安基金"},
            {"code": "000198", "name": "天弘余额宝货币", "type": "货币型", "company": "天弘基金"},
            {"code": "004512", "name": "国联安信心增长纯债", "type": "债券型", "company": "国联安基金"},
            {"code": "001878", "name": "嘉实沪港深精选股票", "type": "股票型", "company": "嘉实基金"},
            {"code": "000961", "name": "天弘沪深300ETF联接", "type": "指数型", "company": "天弘基金"},
        ]