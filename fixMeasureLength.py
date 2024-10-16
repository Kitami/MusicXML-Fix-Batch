import xml.etree.ElementTree as ET
import os
import tkinter as tk
from tkinter import filedialog

def create_rest_element(duration_value, measure):
    rest_element = ET.Element("note")
    rest_element.append(ET.Element("rest"))
    type_element = ET.Element("type")
    
    # 從小節中提取 divisions 元素的值，找不到時設置默認值 4
    divisions_element = measure.find(".//divisions")
    divisions_value = 1/float(divisions_element.text) if divisions_element is not None else 1/4
    
    # 根據休符的 duration_value 計算 duration 元素的值
    duration_element = ET.Element("duration")
    duration_element.text = str(float(duration_value / divisions_value))
    rest_element.append(duration_element)
    
    # 找出比 duration_value 小的最大時值單位
    durations = [d for d in [0.0625, 0.25, 0.125, 0.5] if d <= duration_value]
    
    # 如果沒有符合條件的時值單位，則跳過此小節的處理
    if not durations:
        print(f"跳過處理：duration_value ({duration_value}) 小於最小音符時值，跳過當前小節。")
        return

    max_duration = max(durations)

    # 遞歸處理
    if duration_value != max_duration:
        create_rest_element(max_duration, measure)
        create_rest_element(duration_value - max_duration, measure)
        return
    
    if duration_value == 0.25:
        type_element.text = "quarter"
    elif duration_value == 0.125:
        type_element.text = "eighth"
    elif duration_value == 0.5:
        type_element.text = "half"
    elif duration_value == 0.0625:
        type_element.text = "16th"
    
    rest_element.append(type_element)
    measure.append(rest_element)

def get_note_value(note_elem, divisions_value):
    # 如果音符包含 <chord />，則跳過時值累計
    if note_elem.find("./chord") is not None:
        print("跳過和弦音符的時值計算。")
        return 0  # 不累計和弦音符的時值

    duration_elem = note_elem.find("./duration")
    duration = float(duration_elem.text) / divisions_value / 4
    return duration

def add_voice_to_note(note_elem, voice_number=2):
    """給音符元素增加聲部"""
    voice_elem = note_elem.find("./voice")
    if voice_elem is None:
        voice_elem = ET.Element("voice")
        voice_elem.text = str(voice_number)
        note_elem.append(voice_elem)
    else:
        voice_elem.text = str(voice_number)

def fix_measure_lengths(xml_file_path):
    # 解析 musicxml 文件
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    fixed_measures_count = 0

    # 遍歷每個小節
    for measure in root.findall('.//measure'):
        divisions_elem = measure.find(".//divisions")
        divisions_value = float(divisions_elem.text) if divisions_elem is not None else 1
        
        measure_number = measure.get('number')
        total_duration = 0
        notes = measure.findall('.//note')
        
        forward_elem = measure.find(".//forward")
        if forward_elem:
            forward_duration_elem = forward_elem.find(".//duration")
            forward_value = float(forward_duration_elem.text)
            total_duration += forward_value

        # 遍歷小節中的每個音符
        while notes:
            first_note = notes.pop(0)  # 使用 pop(0) 安全地取得並移除第一個元素
            total_duration += get_note_value(first_note,divisions_value)

            # 處理小節的長度
            if total_duration > 1:
                fixed_measures_count += 1
                measure.remove(first_note)

        # 在每小節處理完後輸出結果
        print(f"小節號碼: {measure_number}, 總長度: {total_duration}", end=', ')

        # 遍歷完所有音符後，處理增加休符
        if total_duration < 1 and total_duration != 0:
            # 增加休符以補充完整一個小節
            rest_duration = 1 - total_duration
            create_rest_element(rest_duration, measure)
            fixed_measures_count += 1
            print(f"增加休符長度: {rest_duration}", end=', ')
        
        # 單獨輸出一個換行
        print()

    # 獲取舊文件的目錄和文件名
    file_dir = os.path.dirname(xml_file_path)  # 輸入文件的目錄
    file_name, file_extension = os.path.splitext(os.path.basename(xml_file_path))

    # 新文件名
    new_file_name = file_name + "_fixed" + file_extension
    new_file_path = os.path.join(file_dir, new_file_name)  # 新文件的完整路徑

    # 將修復後的 musicxml 寫入新文件
    tree.write(new_file_path)

    print(f"處理完成，修復了 {fixed_measures_count} 個小節。新文件保存為 {new_file_path}。")

# 文件選擇 GUI
def select_file():
    root = tk.Tk()
    root.withdraw()  # 隱藏主窗口
    file_path = filedialog.askopenfilename(
        title="選擇目標 XML 文件",
        filetypes=[("XML files", "*.xml *.musicxml")]
    )
    return file_path

# 使用範例
xml_file_path = select_file()
#input("請輸入目標 XML 文件的路徑：")

# 使用範例
fix_measure_lengths(xml_file_path)
