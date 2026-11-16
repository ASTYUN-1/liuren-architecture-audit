import fs from 'node:fs';
import vm from 'node:vm';
import crypto from 'node:crypto';

const engineRoot = new URL('../engine/legacy/', import.meta.url);
const manifest = JSON.parse(fs.readFileSync(new URL('./legacy-engine-manifest.json', import.meta.url), 'utf8'));
const digest = (bytes) => crypto.createHash('sha256').update(bytes).digest('hex');

function loadEngine() {
  const files = {};
  for (const expected of manifest.files) {
    const bytes = fs.readFileSync(new URL(expected.path, engineRoot));
    if (digest(bytes) !== expected.sha256) throw new Error(`ENGINE_HASH_MISMATCH: ${expected.path}; 执行停止，先核实版本。`);
    files[expected.path] = bytes.toString('utf8');
  }
  const noop = () => {};
  const context = vm.createContext({
    console: { log: noop, warn: noop, error: noop },
    window: { addEventListener: noop, indexedDB: { open: () => ({}) } },
    document: { addEventListener: noop },
    setTimeout: noop, clearTimeout: noop, setInterval: noop, clearInterval: noop,
    vm_glob: { USER_ALL_DATA: { pages_config: { zhuti_config: { zhuti_bord_clor: '#cccccc' } } } },
  });
  for (const name of ['js/lunar.js', 'js/data.js', 'js/hexin.js', 'js/api.js', 'js/guize.js', 'js/paipan.js']) {
    vm.runInContext(files[name], context, { filename: name, timeout: 15000 });
  }
  // This helper is an original function in index.js. The complete UI is unnecessary.
  const start = files['index.js'].indexOf('function getCurrentSolarTerm(');
  const end = files['index.js'].indexOf('function enterFullscreenElement(', start);
  if (start < 0 || end < start) throw new Error('ENGINE_HELPER_MISSING: 原节气函数边界未找到。');
  vm.runInContext(files['index.js'].slice(start, end), context, { filename: 'index.js:getCurrentSolarTerm', timeout: 15000 });
  return { context, files };
}

function exportOriginalPage(context, html, P) {
  const marker = html.indexOf('<pre id="paipan-json-ai"');
  const start = html.indexOf('(function() {', marker);
  const end = html.indexOf('</script>', start);
  if (marker < 0 || start < 0 || end < 0) throw new Error('ENGINE_EXPORTER_MISSING: 原JSON导出器未找到。');
  const timers = [];
  const element = { textContent: '' };
  context.vm_paipan = { currentPpdata: [P] };
  context.document.getElementById = (id) => id === 'paipan-json-ai' ? element : null;
  context.setInterval = (fn) => { timers.push(fn); return timers.length; };
  // The original exporter waits for P.id. This is an adapter-only cache key.
  P.id = digest(JSON.stringify(P._D));
  vm.runInContext(html.slice(start, end), context, { filename: 'index.html:original-ai-json-exporter', timeout: 15000 });
  if (timers.length !== 1) throw new Error('ENGINE_EXPORTER_UNEXPECTED: 等待回调数量异常。');
  timers[0]();
  if (timers.length !== 2) throw new Error('ENGINE_EXPORTER_UNEXPECTED: 导出回调未建立。');
  timers[1]();
  if (!element.textContent) throw new Error('ENGINE_EXPORT_FAILED: 原页面未输出JSON。');
  return JSON.parse(element.textContent);
}

function chart(request, context, files) {
  context.__nativeInput = request.native_input;
  // Keep engine input inside its own VM realm and preserve its mutation separately.
  vm.runInContext('__nativeInput = JSON.parse(JSON.stringify(__nativeInput)); __result = LiuRenPaiPan(__nativeInput);', context, { timeout: 20000 });
  const P = context.__result;
  if (!P) throw new Error('ENGINE_EMPTY_RESULT: 原排盘函数未返回盘面。');
  const raw = exportOriginalPage(context, files['index.html'], P);
  return {
    raw,
    native_input_after: JSON.parse(JSON.stringify(P._D)),
    native: {
      userinfo: P.userinfo,
      guiren_type: P.guiren_type,
      zhouye_type: P.zhouye_type,
      // Legacy guiren_zhouye is based on the hour even if a fixed setting is used.
      hour_based_zhouye_label: P.guiren_zhouye,
      guiren_shunni_label: P.guiren_shunni,
      guiren: P.shensha_list?.dg?.贵人,
      lianmu: P.shensha_list?.dg?.帘幕,
      richangsheng: P.richangsheng,
      branch_growth: P._zi_cs,
      transmission_earth_positions: P.sanchuan_dipan,
      seasonal_strength: P.wangshuai,
      solar_terms_same_minute: P.jieqi?.list?.filter((term) => term.y === Number(P._D.Date.slice(0,4)) && term.m === Number(P._D.Date.slice(5,7)) && term.d === Number(P._D.Date.slice(8,10)) && term.h === Number(P._D.Time.slice(0,2)) && term.i === Number(P._D.Time.slice(3,5))) || [],
    },
  };
}

function calendar(request, context) {
  const days = [];
  const first = Date.parse(`${request.start}T12:00:00+08:00`);
  const last = Date.parse(`${request.end}T12:00:00+08:00`);
  for (let stamp = first; stamp <= last; stamp += 86400000) {
    const localDate = new Date(stamp);
    context.__calendarDate = [localDate.getFullYear(), localDate.getMonth() + 1, localDate.getDate()];
    const pillars = vm.runInContext('Solar.fromYmdHms(...__calendarDate, 12, 0, 30).getLunar().getBaZi()', context);
    const date = `${context.__calendarDate[0]}-${String(context.__calendarDate[1]).padStart(2, '0')}-${String(context.__calendarDate[2]).padStart(2, '0')}`;
    if (request.day_branches?.length && !request.day_branches.includes(pillars[2][1])) continue;
    if (request.day_pillars?.length && !request.day_pillars.includes(pillars[2])) continue;
    days.push({ date, day_pillar: pillars[2], day_branch: pillars[2][1], pillars: Array.from(pillars), sample_time: '12:00:30+08:00' });
  }
  return { schema: 'liuren-calendar-candidates-v1', start: request.start, end: request.end, days, timezone: 'Asia/Shanghai', method: 'original Solar.getLunar().getBaZi(); noon sample, no event prediction' };
}

try {
  if (process.env.TZ !== 'Asia/Shanghai') throw new Error('ENGINE_TIMEZONE_MISMATCH');
  const request = JSON.parse(fs.readFileSync(0, 'utf8'));
  const { context, files } = loadEngine();
  const result = request.operation === 'calendar' ? calendar(request, context) : chart(request, context, files);
  process.stdout.write(JSON.stringify({ ok: true, result }));
} catch (error) {
  process.stdout.write(JSON.stringify({ ok: false, error: { code: 'LEGACY_ENGINE_FAILED', message: error.message } }));
  process.exitCode = 1;
}
