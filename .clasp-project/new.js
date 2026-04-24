/**
 * Google Apps Script — 탭 자동 생성 + 데이터 수신
 *
 * 설치:
 * 1. Google Sheets → 확장 프로그램 → Apps Script
 * 2. 기존 코드 전부 지우고 이 코드 붙여넣기
 * 3. 배포 → 배포 관리 → 연필 아이콘(수정) → 새 버전 → 배포
 *
 * 지원 액션:
 *   POST {"id":"G4-1", ...}              — 단일 태스크 upsert
 *   POST {"_action":"bulk", "tasks":[…]}  — 전체 태스크 일괄 동기화
 *   POST {"_action":"reset"}              — 모든 탭 데이터 초기화 (헤더 유지)
 */

// 탭 + 헤더 정의
var SCHEMA = {
  tasks:     ["id","name","desc","status","tier","target","minimum","lang_ratio","cot_ratio","completed","pass_rate","avg_turns"],
  seeds:     ["task_id","name","category","usage","contamination"],
  pipeline:  ["task_id","phase","name","detail","status"],
  issues:    ["task_id","severity","text","date"],
  crossDims: ["task_id","name","target","actual"],
  turnDist:  ["task_id","dim_name","turns","count"]
};

function ensureSheet(ss, name) {
  var sheet = ss.getSheetByName(name);
  if (!sheet) {
    sheet = ss.insertSheet(name);
    sheet.getRange(1, 1, 1, SCHEMA[name].length).setValues([SCHEMA[name]]);
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

    // 모든 탭 자동 생성
    for (var name in SCHEMA) { ensureSheet(ss, name); }

    // 액션 분기
    var action = data._action || "";

    if (action === "reset") {
      return doReset(ss);
    }
    if (action === "bulk") {
      return doBulk(ss, data.tasks || []);
    }

    // 기본: 단일 태스크 upsert
    return doSingleSync(ss, data);
  } catch(err) {
    return resp({error: err.toString()});
  }
}

/** 모든 탭 삭제 후 헤더와 함께 재생성 */
function doReset(ss) {
  for (var name in SCHEMA) {
    var sheet = ss.getSheetByName(name);
    if (sheet) ss.deleteSheet(sheet);
    var newSheet = ss.insertSheet(name);
    newSheet.getRange(1, 1, 1, SCHEMA[name].length).setValues([SCHEMA[name]]);
    var hdr = newSheet.getRange(1, 1, 1, SCHEMA[name].length);
    hdr.setFontWeight("bold");
    hdr.setBackground("#1a1d25");
    hdr.setFontColor("#6c9fff");
  }
  return resp({status:"ok", action:"reset", ts:new Date().toISOString()});
}

/** 여러 태스크를 한 요청으로 일괄 동기화 */
function doBulk(ss, tasks) {
  var results = [];
  for (var t = 0; t < tasks.length; t++) {
    try {
      syncOneTask(ss, tasks[t]);
      results.push({task: tasks[t].id, status: "ok"});
    } catch(err) {
      results.push({task: tasks[t].id, status: "error", msg: err.toString()});
    }
  }
  return resp({status:"ok", action:"bulk", results:results, ts:new Date().toISOString()});
}

/** 단일 태스크 동기화 (외부 진입점) */
function doSingleSync(ss, data) {
  var taskId = data.id;
  if (!taskId) return resp({error: "id 필드 없음"});
  syncOneTask(ss, data);
  return resp({status:"ok", task:taskId, ts:new Date().toISOString()});
}

/** 단일 태스크 동기화 (내부 공통 로직) */
function syncOneTask(ss, data) {
  var taskId = String(data.id).trim();

  upsertTask(ss.getSheetByName("tasks"), taskId, data);

  if (data.seeds) replaceRows(ss.getSheetByName("seeds"), taskId,
    data.seeds.map(function(s){return [taskId, s.name||"", s.category||"", s.usage||"", s.contamination||"-"];}));

  if (data.pipeline) replaceRows(ss.getSheetByName("pipeline"), taskId,
    data.pipeline.map(function(p){return [taskId, p.phase||"", p.name||"", (p.detail||"").replace(/\n/g,", "), p.status||"wait"];}));

  if (data.issues) replaceRows(ss.getSheetByName("issues"), taskId,
    data.issues.map(function(i){return [taskId, i.severity||"info", i.text||"", i.date||""];}));

  if (data.crossDims) replaceRows(ss.getSheetByName("crossDims"), taskId,
    data.crossDims.map(function(d){return [taskId, d.name||"", d.target||0, d.actual||0];}));

  // turnDist: crossDims 내 turnDist 객체를 플랫하게 저장
  if (data.crossDims) {
    var tdRows = [];
    data.crossDims.forEach(function(d) {
      var td = d.turnDist || {};
      for (var turns in td) {
        tdRows.push([taskId, d.name||"", parseInt(turns), td[turns]]);
      }
    });
    replaceRows(ss.getSheetByName("turnDist"), taskId, tdRows);
  }
}

function upsertTask(sheet, taskId, data) {
  var vals = sheet.getDataRange().getValues();
  var rowIdx = -1;
  for (var i = 1; i < vals.length; i++) {
    if (String(vals[i][0]).trim() === taskId) { rowIdx = i + 1; break; }
  }
  var info = data.info || {};
  var ds = data.dataStats || {};
  var row = [
    taskId, data.name||"", data.desc||"", data.status||"wait",
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
  var data = sheet.getDataRange().getValues();
  for (var i = data.length - 1; i >= 1; i--) {
    if (String(data[i][0]).trim() === taskId) sheet.deleteRow(i + 1);
  }
  if (newRows.length > 0) {
    sheet.getRange(sheet.getLastRow() + 1, 1, newRows.length, newRows[0].length).setValues(newRows);
  }
}

function resp(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function doGet(e) {
  return resp({status:"ok", message:"Dashboard webhook running"});
}
