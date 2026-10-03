from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'mes_demo_secret_key_2024'

# 模擬資料結構
class MESData:
    def __init__(self):
        self.production_tasks = [
            {
                'id': 1,
                'name': '產品A組裝',
                'stage': '組裝',
                'status': '待開始',
                'start_time': None,
                'end_time': None,
                'progress': 0
            },
            {
                'id': 2,
                'name': '產品B測試',
                'stage': '測試',
                'status': '待開始',
                'start_time': None,
                'end_time': None,
                'progress': 0
            }
        ]

        self.quality_records = [
            {
                'id': 1,
                'product': '產品A',
                'batch': '批次001',
                'inspector': '張三',
                'check_time': '2024-01-15 10:30',
                'result': '合格',
                'defects': []
            }
        ]

        self.equipment_list = [
            {
                'id': 1,
                'name': '生產線A',
                'type': '組裝線',
                'status': '運行中',
                'last_maintenance': '2024-01-10',
                'next_maintenance': '2024-02-10',
                'maintenance_records': []
            },
            {
                'id': 2,
                'name': '測試設備B',
                'type': '測試儀器',
                'status': '待命',
                'last_maintenance': '2024-01-12',
                'next_maintenance': '2024-02-12',
                'maintenance_records': []
            }
        ]

    def get_production_stats(self):
        total = len(self.production_tasks)
        completed = sum(1 for task in self.production_tasks if task['status'] == '完成')
        in_progress = sum(1 for task in self.production_tasks if task['status'] == '進行中')
        return {
            'total': total,
            'completed': completed,
            'in_progress': in_progress,
            'completion_rate': (completed / total * 100) if total > 0 else 0
        }

    def get_quality_stats(self):
        total = len(self.quality_records)
        qualified = sum(1 for record in self.quality_records if record['result'] == '合格')
        return {
            'total': total,
            'qualified': qualified,
            'unqualified': total - qualified,
            'qualification_rate': (qualified / total * 100) if total > 0 else 0
        }

# 全域資料實例
mes_data = MESData()

@app.route('/')
def index():
    """首頁"""
    stats = {
        'production': mes_data.get_production_stats(),
        'quality': mes_data.get_quality_stats(),
        'equipment': {
            'total': len(mes_data.equipment_list),
            'running': sum(1 for eq in mes_data.equipment_list if eq['status'] == '運行中'),
            'maintenance': sum(1 for eq in mes_data.equipment_list if eq['status'] == '維修中')
        }
    }
    return render_template('index.html', stats=stats)

@app.route('/api/dashboard-stats')
def dashboard_stats():
    """取得首頁儀表板統計資料"""
    return jsonify({
        'production': mes_data.get_production_stats(),
        'quality': mes_data.get_quality_stats(),
        'equipment': {
            'total': len(mes_data.equipment_list),
            'running': sum(1 for eq in mes_data.equipment_list if eq['status'] == '運行中'),
            'maintenance': sum(1 for eq in mes_data.equipment_list if eq['status'] == '維修中')
        }
    })

@app.route('/production')
def production():
    """生產流程監控頁面"""
    return render_template('production.html', tasks=mes_data.production_tasks)

@app.route('/api/production-stats')
def production_stats():
    """取得生產任務統計資料"""
    stats = mes_data.get_production_stats()
    stats.update({
        'running': sum(1 for task in mes_data.production_tasks if task['status'] == '進行中'),
        'paused': sum(1 for task in mes_data.production_tasks if task['status'] == '暫停'),
        'pending': sum(1 for task in mes_data.production_tasks if task['status'] == '待開始')
    })
    return jsonify(stats)

@app.route('/production/update/<int:task_id>', methods=['POST'])
def update_production_task(task_id):
    """更新生產任務狀態"""
    action = request.form.get('action')
    task = next((t for t in mes_data.production_tasks if t['id'] == task_id), None)

    if not task:
        return jsonify({'success': False, 'message': '任務不存在'})

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if action == 'start':
        task['status'] = '進行中'
        task['start_time'] = current_time
        task['progress'] = 10
    elif action == 'pause':
        task['status'] = '暫停'
    elif action == 'resume':
        task['status'] = '進行中'
    elif action == 'complete':
        task['status'] = '完成'
        task['end_time'] = current_time
        task['progress'] = 100
    elif action == 'reset':
        task['status'] = '待開始'
        task['start_time'] = None
        task['end_time'] = None
        task['progress'] = 0

    return jsonify({'success': True, 'task': task})

@app.route('/quality')
def quality():
    """品質管理頁面"""
    stats = mes_data.get_quality_stats()
    return render_template('quality.html', records=mes_data.quality_records, stats=stats)

@app.route('/api/quality-stats')
def quality_stats():
    """取得品質統計資料"""
    return jsonify(mes_data.get_quality_stats())

@app.route('/quality/add', methods=['POST'])
def add_quality_record():
    """添加品質記錄"""
    product = request.form.get('product')
    batch = request.form.get('batch')
    inspector = request.form.get('inspector')
    result = request.form.get('result')
    defects = request.form.getlist('defects[]')

    new_record = {
        'id': len(mes_data.quality_records) + 1,
        'product': product,
        'batch': batch,
        'inspector': inspector,
        'check_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'result': result,
        'defects': defects
    }

    mes_data.quality_records.append(new_record)
    return jsonify({'success': True, 'record': new_record})

@app.route('/equipment')
def equipment():
    """設備維護管理頁面"""
    return render_template('equipment.html', equipment=mes_data.equipment_list)

@app.route('/api/equipment-stats')
def equipment_stats():
    """取得設備狀態統計資料"""
    return jsonify({
        'running': sum(1 for eq in mes_data.equipment_list if eq['status'] == '運行中'),
        'maintenance': sum(1 for eq in mes_data.equipment_list if eq['status'] == '維修中'),
        'standby': sum(1 for eq in mes_data.equipment_list if eq['status'] == '待命')
    })

@app.route('/equipment/update/<int:equipment_id>', methods=['POST'])
def update_equipment_status(equipment_id):
    """更新設備狀態"""
    equipment = next((eq for eq in mes_data.equipment_list if eq['id'] == equipment_id), None)

    if not equipment:
        return jsonify({'success': False, 'message': '設備不存在'})

    action = request.form.get('action')
    current_time = datetime.now().strftime('%Y-%m-%d')

    if action == 'maintenance':
        equipment['status'] = '維修中'
        equipment['last_maintenance'] = current_time
        # 添加維護記錄
        maintenance_record = {
            'date': current_time,
            'type': '定期維護',
            'description': '例行設備維護',
            'technician': '李四'
        }
        equipment['maintenance_records'].append(maintenance_record)
    elif action == 'repair':
        equipment['status'] = '運行中'
    elif action == 'standby':
        equipment['status'] = '待命'

    return jsonify({'success': True, 'equipment': equipment})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
