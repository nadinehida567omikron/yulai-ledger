import os
import json
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
# 云端数据保存的文件
DATA_FILE = 'yulai_cloud_data.json'

# === 完美还原您的原始 HTML 界面 ===
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>禹来日常记账系统 - 云端色彩版</title>
    <style>
        body { font-family: 'Microsoft YaHei', sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h1 { text-align: center; color: #333; }
        .tabs { display: flex; border-bottom: 2px solid #007bff; margin-bottom: 20px; }
        .tab { padding: 10px 20px; cursor: pointer; font-size: 16px; background: #e9ecef; border: none; outline: none; transition: 0.3s; margin-right: 5px; border-radius: 5px 5px 0 0; }
        .tab.active { background: #007bff; color: white; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .form-group { display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 15px; }
        .input-box { flex: 1; min-width: 200px; display: flex; flex-direction: column; }
        label { font-weight: bold; margin-bottom: 5px; font-size: 14px; color: #555; }
        input, select, textarea { padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px; outline: none; }
        button.btn { background-color: #28a745; color: white; border: none; padding: 10px 20px; font-size: 16px; border-radius: 4px; cursor: pointer; width: 100%; margin-top: 10px; }
        button.btn:hover { background-color: #218838; }
        button.btn-export { background-color: #17a2b8; width: auto; margin-bottom: 10px; }
        button.btn-cancel { background-color: #6c757d; display: none; margin-top: 10px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: center; vertical-align: middle; }
        th { background-color: #f8f9fa; color: #333;}
        .action-btn { padding: 4px 8px; margin: 2px; border: none; border-radius: 3px; cursor: pointer; color: white; font-size: 12px; }
        .btn-edit { background-color: #ffc107; color: #000; }
        .btn-delete { background-color: #dc3545; }
        .summary-box { padding: 15px; background: #e9ecef; border-radius: 5px; margin-top: 10px; font-size: 18px; font-weight: bold; color: #333;}
        h3 { color: #007bff; border-bottom: 2px solid #e9ecef; padding-bottom: 5px; margin-top: 25px; }
        .badge { display: inline-block; padding: 4px 10px; border-radius: 12px; font-size: 13px; font-weight: bold; text-align: center; min-width: 60px; }
        select#main_cat { transition: background-color 0.3s, color 0.3s; font-weight: bold; }
    </style>
</head>
<body>

<div class="container">
    <h1>📊 禹来日常记账系统 (云端同步版)</h1>
    
    <div class="tabs">
        <button class="tab active" id="tab-entry" onclick="switchTab('entry')">💰 新增/修改账目</button>
        <button class="tab" id="tab-list" onclick="switchTab('list')">📋 日常台账明细</button>
        <button class="tab" id="tab-summary" onclick="switchTab('summary')">📈 月度汇总</button>
    </div>

    <div id="entry" class="tab-content active">
        <h3 id="form-title" style="margin-top: 0;">✏️ 录入新账目</h3>
        <input type="hidden" id="edit_index" value="-1">
        <input type="hidden" id="original_serial" value="">
        
        <div class="form-group">
            <div class="input-box"><label>时间 (如 2026.01.18)</label><input type="date" id="date"></div>
            <div class="input-box"><label>总类别</label>
                <select id="main_cat" onchange="updateSelectColor()">
                    <option value="接待">接待</option><option value="餐旅">餐旅</option>
                    <option value="经营管理">经营管理</option><option value="办公费用">办公费用</option>
                    <option value="人员薪酬">人员薪酬</option><option value="其他">其他</option>
                </select>
            </div>
            <div class="input-box"><label>子类别 (如：会餐/交通)</label><input type="text" id="sub_cat"></div>
        </div>
        <div class="form-group">
            <div class="input-box"><label>摘要</label><input type="text" id="summary_desc" placeholder="如：东北菜馆"></div>
            <div class="input-box"><label>人员</label><input type="text" id="people" placeholder="如：罗一维、郑磊"></div>
            <div class="input-box"><label>人数</label><input type="number" id="num_people" value="1" min="1"></div>
        </div>
        <div class="form-group">
            <div class="input-box"><label>出发地/目的地</label><input type="text" id="location" placeholder="如：郑州-上海"></div>
            <div class="input-box"><label>金额 (元)</label><input type="number" id="amount" step="0.01"></div>
            <div class="input-box"><label>申请人</label><input type="text" id="applicant"></div>
        </div>
        <div class="form-group">
            <div class="input-box"><label>申报状态</label>
                <select id="status"><option>未申报</option><option>已申报</option><option>审批中</option></select>
            </div>
            <div class="input-box" style="flex: 2;"><label>备注</label><input type="text" id="remarks"></div>
        </div>
        
        <div style="display: flex; gap: 10px;">
            <button class="btn" id="save-btn" onclick="saveRecord()">保存记录</button>
            <button class="btn btn-cancel" id="cancel-btn" onclick="cancelEdit()">取消修改</button>
        </div>
    </div>

    <div id="list" class="tab-content">
        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
            <button class="btn btn-export" onclick="exportCSV()">📥 导出为 Excel (CSV)</button>
            <button class="btn btn-export" style="background:#dc3545;" onclick="clearAllData()">🗑️ 清空所有数据</button>
        </div>
        <table id="dataTable">
            <thead>
                <tr>
                    <th>月份</th><th>序号</th><th>时间</th><th>总类别</th><th>子类别</th><th>摘要</th>
                    <th>人员</th><th>金额</th><th>申请人</th><th>操作</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>
    </div>

    <div id="summary" class="tab-content">
        <div class="summary-box" id="totalAmount">年度总支出累计: 0.00 元</div>
        
        <h3>📅 月度总支出汇总</h3>
        <table id="monthlySummaryTable">
            <thead>
                <tr><th>月份</th><th>当月总支出 (元)</th></tr>
            </thead>
            <tbody></tbody>
        </table>

        <h3>🏷️ 各类别支出明细</h3>
        <table id="summaryTable">
            <thead>
                <tr><th>总类别</th><th>子类别</th><th>累计金额 (元)</th></tr>
            </thead>
            <tbody></tbody>
        </table>
    </div>
</div>

<script>
    const catColors = {
        "接待": { bg: "#e3f2fd", text: "#0d47a1" }, "餐旅": { bg: "#e8f5e9", text: "#1b5e20" },
        "经营管理": { bg: "#fff3e0", text: "#e65100" }, "办公费用": { bg: "#f3e5f5", text: "#4a148c" },
        "人员薪酬": { bg: "#ffebee", text: "#b71c1c" }, "其他": { bg: "#f5f5f5", text: "#424242" }
    };
    const monthColors = {
        "01": { bg: "#e1bee7", text: "#4a148c" }, "02": { bg: "#c5cae9", text: "#1a237e" },
        "03": { bg: "#b3e5fc", text: "#01579b" }, "04": { bg: "#b2dfdb", text: "#004d40" },
        "05": { bg: "#dcedc8", text: "#33691e" }, "06": { bg: "#fff9c4", text: "#f57f17" },
        "07": { bg: "#ffecb3", text: "#ff6f00" }, "08": { bg: "#ffe0b2", text: "#e65100" },
        "09": { bg: "#ffccbc", text: "#bf360c" }, "10": { bg: "#d7ccc8", text: "#3e2723" },
        "11": { bg: "#cfd8dc", text: "#263238" }, "12": { bg: "#f5f5f5", text: "#212121" }
    };

    function updateSelectColor() {
        const select = document.getElementById('main_cat');
        const colorConfig = catColors[select.value] || catColors["其他"];
        select.style.backgroundColor = colorConfig.bg;
        select.style.color = colorConfig.text;
    }

    function getBadgeHTML(category) {
        const colorConfig = catColors[category || "其他"] || catColors["其他"];
        return `<span class="badge" style="background-color: ${colorConfig.bg}; color: ${colorConfig.text};">${category || "其他"}</span>`;
    }

    function getMonthBadgeHTML(month) {
        const colorConfig = monthColors[month || "01"] || { bg: "#e0e0e0", text: "#333" };
        return `<span class="badge" style="background-color: ${colorConfig.bg}; color: ${colorConfig.text};">${parseInt(month || "01")} 月</span>`;
    }

    document.getElementById('date').valueAsDate = new Date();
    updateSelectColor(); 
    
    // --- 【云端核心】: 替换了原本的本地存储 ---
    let records = [];
    
    function loadDataFromServer() {
        fetch('/api/data')
            .then(res => res.json())
            .then(data => {
                records = data;
                renderTable();
                renderSummary();
            })
            .catch(err => console.error("加载云端数据失败", err));
    }
    
    function syncToServer() {
        fetch('/api/data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(records)
        }).then(res => {
            if(!res.ok) alert("⚠️ 云端同步可能失败，请检查网络！");
        });
    }

    // 页面加载时自动获取云端数据
    loadDataFromServer();

    function switchTab(tabId) {
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.getElementById(tabId).classList.add('active');
        document.getElementById('tab-' + tabId).classList.add('active');
        if(tabId === 'list') renderTable();
        if(tabId === 'summary') renderSummary();
    }

    function saveRecord() {
        const dateVal = document.getElementById('date').value;
        if(!dateVal || !document.getElementById('amount').value) return alert('时间和金额为必填项！');

        const editIndex = parseInt(document.getElementById('edit_index').value);
        const d = new Date(dateVal);
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const yearMonth = String(d.getFullYear()).slice(2) + month; 
        const timeStr = dateVal.replace(/-/g, '.');

        let serial = "";
        if (editIndex > -1) {
            serial = document.getElementById('original_serial').value;
        } else {
            const currentMonthRecords = records.filter(r => r.month === month);
            serial = "CL" + yearMonth + String(currentMonthRecords.length + 1).padStart(3, '0');
        }

        const record = {
            month: month, serial: serial, time: timeStr, dateRaw: dateVal,
            main_cat: document.getElementById('main_cat').value, sub_cat: document.getElementById('sub_cat').value,
            summary: document.getElementById('summary_desc').value, people: document.getElementById('people').value,
            num_people: document.getElementById('num_people').value, location: document.getElementById('location').value,
            amount: parseFloat(document.getElementById('amount').value).toFixed(2), applicant: document.getElementById('applicant').value,
            status: document.getElementById('status').value, remarks: document.getElementById('remarks').value
        };

        if (editIndex > -1) {
            records[editIndex] = record;
            alert('✅ 记录修改成功！');
            cancelEdit(); 
            switchTab('list'); 
        } else {
            records.push(record);
            alert('✅ 保存成功！自动生成序号: ' + serial);
            document.getElementById('sub_cat').value = ''; document.getElementById('amount').value = '';
            document.getElementById('summary_desc').value = ''; document.getElementById('remarks').value = '';
        }
        
        // 自动同步到云端
        syncToServer();
    }

    function renderTable() {
        const tbody = document.querySelector('#dataTable tbody');
        tbody.innerHTML = '';
        records.forEach((r, index) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${getMonthBadgeHTML(r.month)}</td><td>${r.serial}</td><td>${r.time}</td>
                            <td>${getBadgeHTML(r.main_cat)}</td><td>${r.sub_cat}</td><td>${r.summary}</td>
                            <td>${r.people}</td><td><b style="color:#d32f2f;">${r.amount}</b></td><td>${r.applicant}</td>
                            <td>
                                <button class="action-btn btn-edit" onclick="editRecord(${index})">修改</button>
                                <button class="action-btn btn-delete" onclick="deleteRecord(${index})">删除</button>
                            </td>`;
            tbody.appendChild(tr);
        });
    }

    function editRecord(index) {
        const r = records[index];
        if(r.dateRaw) { document.getElementById('date').value = r.dateRaw; }
        document.getElementById('main_cat').value = r.main_cat; updateSelectColor(); 
        document.getElementById('sub_cat').value = r.sub_cat; document.getElementById('summary_desc').value = r.summary;
        document.getElementById('people').value = r.people; document.getElementById('num_people').value = r.num_people || 1;
        document.getElementById('location').value = r.location || ''; document.getElementById('amount').value = r.amount;
        document.getElementById('applicant').value = r.applicant; document.getElementById('status').value = r.status;
        document.getElementById('remarks').value = r.remarks || '';
        document.getElementById('edit_index').value = index; document.getElementById('original_serial').value = r.serial;
        document.getElementById('form-title').innerHTML = `⚠️ 正在修改账目：${r.serial}`; document.getElementById('form-title').style.color = '#ffc107';
        document.getElementById('save-btn').innerText = '确认修改'; document.getElementById('cancel-btn').style.display = 'block';
        switchTab('entry');
    }

    function cancelEdit() {
        document.getElementById('edit_index').value = "-1"; document.getElementById('original_serial').value = "";
        document.getElementById('form-title').innerHTML = `✏️ 录入新账目`; document.getElementById('form-title').style.color = '#007bff';
        document.getElementById('save-btn').innerText = '保存记录'; document.getElementById('cancel-btn').style.display = 'none';
        document.getElementById('sub_cat').value = ''; document.getElementById('summary_desc').value = '';
        document.getElementById('amount').value = ''; document.getElementById('remarks').value = '';
    }

    function deleteRecord(index) {
        if(confirm(`⚠️ 确定要删除单号为 ${records[index].serial} 的账目吗？删除后不可恢复。`)) {
            records.splice(index, 1);
            syncToServer();
            renderTable();
        }
    }

    function renderSummary() {
        let total = 0; let summaryData = {}; let monthlyData = {};
        records.forEach(r => {
            let amt = parseFloat(r.amount); total += amt;
            let main = r.main_cat || '未分类'; let sub = r.sub_cat || '未分类'; let key = main + '|' + sub; 
            if(!summaryData[key]) { summaryData[key] = { main_cat: main, sub_cat: sub, amount: 0 }; }
            summaryData[key].amount += amt;
            if(!monthlyData[r.month]) { monthlyData[r.month] = 0; }
            monthlyData[r.month] += amt;
        });
        document.getElementById('totalAmount').innerText = `年度总支出累计: ${total.toFixed(2)} 元`;
        const mBody = document.querySelector('#monthlySummaryTable tbody'); mBody.innerHTML = '';
        Object.keys(monthlyData).sort().forEach(m => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${getMonthBadgeHTML(m)}</td><td><b style="color:#d32f2f;">${monthlyData[m].toFixed(2)}</b></td>`;
            mBody.appendChild(tr);
        });
        const tbody = document.querySelector('#summaryTable tbody'); tbody.innerHTML = '';
        for (const key in summaryData) {
            const data = summaryData[key]; const tr = document.createElement('tr');
            tr.innerHTML = `<td>${getBadgeHTML(data.main_cat)}</td><td>${data.sub_cat}</td><td><b>${data.amount.toFixed(2)}</b></td>`;
            tbody.appendChild(tr);
        }
    }

    function exportCSV() {
        if(records.length === 0) return alert('暂无数据导出');
        let csvContent = "\uFEFF月份,序号,时间,总类别,子类别,摘要,人员,人数,出发地/目的地,金额,申请人,申报状态,备注\n";
        records.forEach(r => {
            let row = [r.month, r.serial, r.time, r.main_cat, r.sub_cat, r.summary, r.people, r.num_people, r.location, r.amount, r.applicant, r.status, r.remarks];
            csvContent += row.map(v => `"${v || ''}"`).join(",") + "\n";
        });
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement("a"); link.href = URL.createObjectURL(blob);
        link.download = "禹来日常台账导出.csv"; link.click();
    }
    
    function clearAllData() {
        if(confirm('⚠️ 警告：此操作将清空所有数据且不可恢复！是否确认清空？')) {
            records = [];
            syncToServer();
            renderTable();
            alert('数据已清空。');
        }
    }
</script>
</body>
</html>
"""

@app.route('/')
def index():
    # 直接在网页上呈现完美的 HTML
    return render_template_string(HTML_CONTENT)

@app.route('/api/data', methods=['GET'])
def get_data():
    # 云端读取数据
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                return jsonify(json.load(f))
            except:
                return jsonify([])
    return jsonify([])

@app.route('/api/data', methods=['POST'])
def save_data():
    # 云端保存数据
    records = request.json
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    # 自动获取云平台分配的端口
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
