/**
 * Google Apps Script — Google Sheets에 배포.
 *
 * 설치 방법:
 * 1. Google Sheets → 확장 프로그램 → Apps Script
 * 2. 이 코드 전체를 복사하여 붙여넣기
 * 3. 배포 → 새 배포 → 웹 앱
 *    - 실행 사용자: 나
 *    - 액세스 권한: 모든 사용자
 * 4. 배포 → URL 복사
 * 5. 진행자들에게 환경변수로 전달:
 *    DASHBOARD_WEBHOOK_URL=https://script.google.com/macros/s/xxxxx/exec
 */

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var taskId = data.id;
    if (!taskId) return resp({error: "id 필드 없음"});

    // 1. tasks 탭 업데이트
    upsertTask(ss.getSheetByName("tasks"), data);

    // 2. seeds 탭 업데이트
    if (data.seeds) replaceRows(ss.getSheetByName("seeds"), "task_id", taskId,
      data.seeds.map(function(s) { return [taskId, s.name, s.category, s.usage, s.contamination || "-"]; }),
      ["task_id", "name", "category", "usage", "contamination"]
    );

    // 3. pipeline 탭 업데이트
    if (data.pipeline) replaceRows(ss.getSheetByName("pipeline"), "task_id", taskId,
      data.pipeline.map(function(p) { return [taskId, p.phase, p.name, (p.detail||"").replace(/\n/g, ", "), p.status]; }),
      ["task_id", "phase", "name", "detail", "status"]
    );

    // 4. issues 탭 업데이트
    if (data.issues) replaceRows(ss.getSheetByName("issues"), "task_id", taskId,
      data.issues.map(function(i) { return [taskId, i.severity, i.text, i.date]; }),
      ["task_id", "severity", "text", "date"]
    );

    // 5. crossDims 탭 업데이트
    if (data.crossDims) replaceRows(ss.getSheetByName("crossDims"), "task_id", taskId,
      data.crossDims.map(function(d) { return [taskId, d.name, d.target, d.actual]; }),
      ["task_id", "name", "target", "actual"]
    );

    return resp({status: "ok", task: taskId});
  } catch (err) {
    return resp({error: err.toString()});
  }
}

function upsertTask(sheet, data) {
  if (!sheet) return;
  var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  var idCol = headers.indexOf("id");
  if (idCol === -1) return;

  // 기존 행 찾기
  var vals = sheet.getDataRange().getValues();
  var rowIdx = -1;
  for (var i = 1; i < vals.length; i++) {
    if (vals[i][idCol] === data.id) { rowIdx = i + 1; break; }
  }

  var info = data.info || {};
  var ds = data.dataStats || {};
  var row = [
    data.id, data.name || "", data.desc || "", data.status || "wait",
    info.tier || "", info.target || "", info.minimum || "",
    info.lang_ratio || "", info.cot_ratio || "",
    ds.completed || 0, ds.pass_rate || 0, ds.avg_turns || 0
  ];

  if (rowIdx > 0) {
    sheet.getRange(rowIdx, 1, 1, row.length).setValues([row]);
  } else {
    sheet.appendRow(row);
  }
}

function replaceRows(sheet, keyCol, keyVal, newRows, headers) {
  if (!sheet) return;

  // 헤더가 없으면 추가
  if (sheet.getLastRow() === 0 && headers) {
    sheet.appendRow(headers);
  }

  // 기존 행 삭제 (아래서부터)
  var data = sheet.getDataRange().getValues();
  var colIdx = data[0].indexOf(keyCol);
  if (colIdx === -1) return;

  for (var i = data.length - 1; i >= 1; i--) {
    if (data[i][colIdx] === keyVal) {
      sheet.deleteRow(i + 1);
    }
  }

  // 새 행 추가
  newRows.forEach(function(row) {
    sheet.appendRow(row);
  });
}

function resp(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

// GET 요청 테스트용
function doGet(e) {
  return resp({status: "ok", message: "Dashboard webhook is running"});
}
