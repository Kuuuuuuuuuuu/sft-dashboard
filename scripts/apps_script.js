/**
 * Google Apps Script — 탭 자동 생성 + 데이터 수신
 *
 * 설치:
 * 1. Google Sheets → 확장 프로그램 → Apps Script
 * 2. 기존 코드 전부 지우고 이 코드 붙여넣기
 * 3. 배포 → 배포 관리 → 연필 아이콘(수정) → 새 버전 → 배포
 */

// 탭 + 헤더 정의
var SCHEMA = {
  tasks:     ["id","name","desc","status","tier","target","minimum","lang_ratio","cot_ratio","completed","pass_rate","avg_turns"],
  seeds:     ["task_id","name","category","usage","contamination"],
  pipeline:  ["task_id","phase","name","detail","status"],
  issues:    ["task_id","severity","text","date"],
  crossDims: ["task_id","name","target","actual"]
};

function ensureSheet(ss, name) {
  var sheet = ss.getSheetByName(name);
  if (!sheet) {
    sheet = ss.insertSheet(name);
    sheet.getRange(1, 1, 1, SCHEMA[name].length).setValues([SCHEMA[name]]);
    // 헤더 스타일
    var hdr = sheet.getRange(1, 1, 1, SCHEMA[name].length);
    hdr.setFontWeight("bold");
    hdr.setBackground("#1a1d25");
    hdr.setFontColor("#6c9fff");
  }
  return sheet;
}

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var taskId = data.id;
    if (!taskId) return resp({error: "id 필드 없음"});

    // 모든 탭 자동 생성
    for (var name in SCHEMA) { ensureSheet(ss, name); }

    // 1. tasks
    upsertTask(ss.getSheetByName("tasks"), data);

    // 2. seeds
    if (data.seeds) replaceRows(ss.getSheetByName("seeds"), taskId,
      data.seeds.map(function(s){return [taskId, s.name||"", s.category||"", s.usage||"", s.contamination||"-"];}));

    // 3. pipeline
    if (data.pipeline) replaceRows(ss.getSheetByName("pipeline"), taskId,
      data.pipeline.map(function(p){return [taskId, p.phase||"", p.name||"", (p.detail||"").replace(/\n/g,", "), p.status||"wait"];}));

    // 4. issues
    if (data.issues) replaceRows(ss.getSheetByName("issues"), taskId,
      data.issues.map(function(i){return [taskId, i.severity||"info", i.text||"", i.date||""];}));

    // 5. crossDims
    if (data.crossDims) replaceRows(ss.getSheetByName("crossDims"), taskId,
      data.crossDims.map(function(d){return [taskId, d.name||"", d.target||0, d.actual||0];}));

    return resp({status:"ok", task:taskId, ts:new Date().toISOString()});
  } catch(err) {
    return resp({error: err.toString()});
  }
}

function upsertTask(sheet, data) {
  var vals = sheet.getDataRange().getValues();
  var rowIdx = -1;
  for (var i=1; i<vals.length; i++) {
    if (vals[i][0] === data.id) { rowIdx = i+1; break; }
  }
  var info = data.info || {};
  var ds = data.dataStats || {};
  var row = [
    data.id, data.name||"", data.desc||"", data.status||"wait",
    info.tier||"", info.target||"", info.minimum||"",
    info.lang_ratio||"", info.cot_ratio||"",
    ds.completed||0, ds.pass_rate||0, ds.avg_turns||0
  ];
  if (rowIdx > 0) {
    sheet.getRange(rowIdx, 1, 1, row.length).setValues([row]);
  } else {
    sheet.appendRow(row);
  }
}

function replaceRows(sheet, taskId, newRows) {
  // 기존 행 삭제
  var data = sheet.getDataRange().getValues();
  for (var i=data.length-1; i>=1; i--) {
    if (data[i][0] === taskId) sheet.deleteRow(i+1);
  }
  // 새 행 추가
  newRows.forEach(function(row){ sheet.appendRow(row); });
}

function resp(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function doGet(e) {
  return resp({status:"ok", message:"Dashboard webhook running"});
}
