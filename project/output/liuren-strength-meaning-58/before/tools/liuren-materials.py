"""Fixed local material operations. No arbitrary shell, root path or script parameters."""
import argparse
import json
from types import SimpleNamespace
import uuid
import shutil
import subprocess
from liuren_material_scope import ROOT, MaterialScope
import importlib.util


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', required=True)
    request = json.loads(parser.parse_args().request)
    action = request.get('action')
    scope = MaterialScope()
    if action == 'scope':
        print(json.dumps(scope.describe(), ensure_ascii=False, indent=2))
    elif action in ('book_search', 'book_outline'):
        from liuren_book_search import BookSearch
        search = BookSearch(ROOT, scope.permitted)
        if action == 'book_outline':
            result = search.outline(request.get('book'))
        else:
            result = search.search(request.get('query', ''), queries=request.get('queries'),
                                   book=request.get('book'), limit=request.get('limit', 4),
                                   max_chars=request.get('max_chars', 14000))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif action == 'shensha':
        # Only existing archived charts or scoped generated charts, never arbitrary JSON/config.
        from pathlib import Path
        filename = request.get('path')
        if not isinstance(filename, str) or not filename.strip():
            raise ValueError('shensha需要原课盘JSON路径')
        chart = Path(filename)
        if not chart.is_absolute():
            chart = ROOT / chart
        chart = chart.resolve()
        if (not scope.permitted(chart) or not chart.is_file() or chart.suffix.lower() != '.json'
                or not any(chart.is_relative_to(p.resolve()) for p in [scope.charts, scope.generated])):
            raise ValueError('shensha仅复用排盘存档/六壬或tmp/liuren-materials中的JSON课盘')
        if chart.stat().st_size > 4 * 1024 * 1024:
            raise ValueError('课盘超过4MiB，需检查是否选错文件')
        node = shutil.which('node')
        if not node:
            raise ValueError('没有找到本机Node；不以引擎未核标签回退采用')
        result = subprocess.run([node, str(ROOT/'tools/liuren-shensha.mjs'), '--chart', str(chart)],
                                cwd=ROOT, capture_output=True, text=True, encoding='utf-8',
                                timeout=30, shell=False)
        if result.returncode:
            raise ValueError(result.stderr.strip() or '神煞采用核算失败')
        print(result.stdout, end='')
    elif action in ('scan', 'read'):
        result = scope.scan(request.get('library'), request.get('query', ''), request.get('limit', 40)) if action == 'scan' else scope.read(request.get('path', ''), request.get('start', 1), request.get('count', 160))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif action in ('method', 'methods', 'retrieve'):
        spec = importlib.util.spec_from_file_location('local_material_read', ROOT / 'tools/liuren-local-read.py')
        helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helper)
        if action == 'method':
            if request.get('modules'):
                modules=request['modules']
                if request.get('module') or not isinstance(modules,list) or not 1 <= len(modules) <= 4 or any(not isinstance(k,str) or not k for k in modules):
                    raise ValueError('method的modules为1..4个模块ID，与module二选一')
                for key in dict.fromkeys(modules):
                    helper.print_method(key)
                return
            key = request.get('module')
            if not isinstance(key, str) or not key.strip():
                raise ValueError('method需要明确的module ID，例如relationship或movement')
            helper.print_method(key)
        elif action == 'methods':
            if request.get('plan_id') and not any(
                    name in request for name in ('domains', 'conditions', 'timing', 'nianming')):
                raise ValueError('旧批次接口的plan_id不恢复路由；须重传domains/conditions/timing/nianming。'
                                 '普通研判请用action=method、module=当前步骤模块ID，不重读全计划。')
            helper.print_methods(SimpleNamespace(domain=request.get('domains', []), timing=request.get('timing', False),
                condition=request.get('conditions', []), nianming=request.get('nianming', False), batch=[request.get('batch', 1)],
                context_key=request.get('_context_key'), plan_id=request.get('plan_id'),
                full_plan=request.get('full_plan', False)))
        else:
            limit = request.get('limit', 8)
            if not 1 <= limit <= 50:
                raise ValueError('retrieve limit within 1..50; narrow queries rather than dump the corpus')
            case_query = request.get('case_query') or request.get('query', '')
            exp_query = request.get('experience_query') or request.get('query', '')
            if not case_query.strip() or not exp_query.strip():
                raise ValueError('需要针对争点的查询词')
            out = scope.generated / (str(uuid.uuid4()) + '.json')
            _, text = helper.parallel_search(case_query, exp_query, request.get('category', ''), limit, out)
            print(text, end='')
    else:
        raise ValueError('unknown material action')


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8', newline='')
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        print('LIUREN_MATERIAL_ERROR: ' + str(exc), file=sys.stderr)
        sys.exit(2)
