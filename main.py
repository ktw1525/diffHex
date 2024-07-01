import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk 
import binascii

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

class HexDiffApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hex Diff Tool")
        self.root.geometry("1900x800")  # 창 크기 설정
        self.root.resizable(False, True)  # 가로 크기 조절 비활성화, 세로 크기 조절 활성화
        self.file1_content = None
        self.file2_content = None
        self.search_term = None
        self.search_results1 = []
        self.search_results2 = []
        self.current_result = -1
        self.resize_after_id = None  # 타이머 ID를 저장할 변수

        # 파일 선택 버튼 및 라벨
        frame1 = tk.Frame(root)
        frame1.pack(pady=1, fill='both')

        self.create_file_select_buttons(frame1)

        # 로고 추가
        self.add_logo(frame1)

        frame_buttons = tk.Frame(root)
        frame_buttons.pack(pady=3, fill='both')

        self.create_control_buttons(frame_buttons)

        # 텍스트 위젯 설정 및 미니맵 추가
        text_frame = tk.Frame(root)
        text_frame.pack(expand=True, fill='both')
        
        self.text_area1 = tk.Text(text_frame, wrap='none', bg='white')
        self.text_area2 = tk.Text(text_frame, wrap='none', bg='white')
        
        self.text_area1.grid(row=0, column=0, sticky="nsew")
        self.text_area2.grid(row=0, column=1, sticky="nsew")

        self.canvas1 = tk.Canvas(text_frame, width=100, bg='gray')
        self.canvas1.grid(row=0, column=2, sticky="ns")
        self.canvas2 = tk.Canvas(text_frame, width=100, bg='gray')
        self.canvas2.grid(row=0, column=3, sticky="ns")

        # 열의 너비를 수동으로 설정
        text_frame.grid_columnconfigure(0, weight=1, minsize=800)  # 첫 번째 열의 최소 너비 설정
        text_frame.grid_columnconfigure(1, weight=1, minsize=800)  # 두 번째 열의 최소 너비 설정
        text_frame.grid_rowconfigure(0, weight=1)

        # 스크롤바 설정
        self.scrollbar_y2 = tk.Scrollbar(self.text_area2, orient="vertical", command=self.on_scrollbar_y2)
        self.scrollbar_y2.pack(side="right", fill="y")
        self.text_area2.configure(yscrollcommand=self.scrollbar_y2.set)

        # 스크롤 및 커서 이동 동기화
        self.text_area1.bind('<MouseWheel>', self.sync_scroll)
        self.text_area2.bind('<MouseWheel>', self.sync_scroll)
        self.text_area1.bind('<Key>', self.sync_cursor)
        self.text_area2.bind('<Key>', self.sync_cursor)
        self.scrollbar_y2.config(command=self.on_scrollbar_y2)

        # text_area2의 스크롤 값 변경 시 text_area1 동기화
        self.text_area2.configure(yscrollcommand=self.on_yscroll2)
        self.text_area1.configure(yscrollcommand=self.on_yscroll1)

        # 미니맵 클릭 이벤트 바인딩
        self.canvas1.bind("<Button-1>", self.minimap_click)
        self.canvas2.bind("<Button-1>", self.minimap_click)
        self.canvas1.bind("<B1-Motion>", self.minimap_click)
        self.canvas2.bind("<B1-Motion>", self.minimap_click)

         # text_area1 크기 변경 이벤트 바인딩
        self.text_area1.bind("<Configure>", self.onResizeWindow)

    def create_file_select_buttons(self, frame1):
        self.btn_open_file1 = tk.Button(frame1, text="Open File 1", command=self.load_file1)
        self.btn_open_file1.grid(row=0, column=0)
        self.file1_label = tk.Label(frame1, text="", anchor='w', borderwidth=1, relief="solid", bg="white")
        self.file1_label.grid(pady=0, padx=10, row=0, column=1, sticky='ew')

        self.btn_open_file2 = tk.Button(frame1, text="Open File 2", command=self.load_file2)
        self.btn_open_file2.grid(row=0, column=2)
        self.file2_label = tk.Label(frame1, text="", anchor='w', borderwidth=1, relief="solid", bg="white")
        self.file2_label.grid(pady=0, padx=10, row=0, column=3, sticky='ew')

        frame1.grid_columnconfigure(1, weight=1, minsize=750)  # 두 번째 열의 최소 너비 설정
        frame1.grid_columnconfigure(3, weight=1, minsize=750)  # 두 번째 열의 최소 너비 설정   

    def add_logo(self, frame1):
        self.logo_image = Image.open(resource_path("logo.png"))
        self.logo_image = self.logo_image.resize((100, 50), Image.ANTIALIAS)
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)

        self.logo_frame = tk.Frame(frame1, highlightbackground="black", highlightthickness=1)
        self.logo_frame.grid(padx=90, row=0, column=5)

        self.logo_label = tk.Label(self.logo_frame, image=self.logo_photo)
        self.logo_label.grid(padx=0, row=0, column=5)

    def create_control_buttons(self, frame_buttons):
        self.btn_compare = tk.Button(frame_buttons, text="Compare Files", command=self.compare_files)
        self.btn_compare.grid(row=0, column=0)

        self.btn_find = tk.Button(frame_buttons, text="Find", command=self.find_text, state=tk.DISABLED)
        self.btn_find.grid(row=0, column=1)

        self.btn_back = tk.Button(frame_buttons, text="Back", command=self.find_previous, state=tk.DISABLED)
        self.btn_back.grid(row=0, column=2)

        self.btn_next = tk.Button(frame_buttons, text="Next", command=self.find_next, state=tk.DISABLED)
        self.btn_next.grid(row=0, column=3)

        # Next 버튼 오른쪽에 여백을 추가하고 두 개의 저장 버튼 추가
        self.btn_save1 = tk.Button(frame_buttons, text="Save File 1", command=self.save_file1)
        self.btn_save1.grid(row=0, column=4, padx=(20, 5))

        self.btn_save2 = tk.Button(frame_buttons, text="Save File 2", command=self.save_file2)
        self.btn_save2.grid(row=0, column=5, padx=(5, 20))

    def on_yscroll2(self, *args):
        self.text_area1.yview_moveto(args[0])
        self.scrollbar_y2.set(*args)
        self.update_minimap_scrollbar(self.canvas1, self.text_area1)
        self.update_minimap_scrollbar(self.canvas2, self.text_area2)

    def on_yscroll1(self, *args):
        self.text_area2.yview_moveto(args[0])
        self.scrollbar_y2.set(*args)
        self.update_minimap_scrollbar(self.canvas1, self.text_area1)
        self.update_minimap_scrollbar(self.canvas2, self.text_area2)

    def on_scrollbar_y2(self, *args):
        self.text_area2.yview(*args)
        self.text_area1.yview_moveto(args[1] if args[0] == 'moveto' else self.text_area2.yview()[0])
        self.update_minimap_scrollbar(self.canvas1, self.text_area1)
        self.update_minimap_scrollbar(self.canvas2, self.text_area2)

    def sync_scroll(self, event):
        delta = -1 if event.delta > 0 else 1
        self.text_area1.yview_scroll(delta, "units")
        self.text_area2.yview_scroll(delta, "units")
        self.update_minimap(self.canvas1, self.text_area1)
        self.update_minimap(self.canvas2, self.text_area2)
        self.update_minimap_scrollbar(self.canvas1, self.text_area1)
        self.update_minimap_scrollbar(self.canvas2, self.text_area2)
        return "break"

    def sync_cursor(self, event):
        index = event.widget.index(tk.INSERT)
        other = self.text_area2 if event.widget == self.text_area1 else self.text_area1
        other.mark_set(tk.INSERT, index)
        other.see(tk.INSERT)
        self.update_minimap(self.canvas1, self.text_area1)
        self.update_minimap(self.canvas2, self.text_area2)
        self.update_minimap_scrollbar(self.canvas1, self.text_area1)
        self.update_minimap_scrollbar(self.canvas2, self.text_area2)

    def minimap_click(self, event):
        canvas = event.widget
        canvas_height = int(canvas.winfo_height())
        click_position = event.y / canvas_height
        self.text_area1.yview_moveto(click_position)
        self.text_area2.yview_moveto(click_position)
        self.update_minimap_scrollbar(self.canvas1, self.text_area1)
        self.update_minimap_scrollbar(self.canvas2, self.text_area2)

    def load_file1(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, 'rb') as file:
                self.file1_content = file.read()
            self.file1_label.config(text=file_path)
            self.show_files(self.text_area1, self.canvas1, self.file1_content)
            messagebox.showinfo("File 1", "File 1 loaded successfully!")

    def load_file2(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, 'rb') as file:
                self.file2_content = file.read()
            self.file2_label.config(text=file_path)
            self.show_files(self.text_area2, self.canvas2, self.file2_content)
            messagebox.showinfo("File 2", "File 2 loaded successfully!")

    def save_file1(self):
        self.save_file(self.text_area1, "Save File 1")

    def save_file2(self):
        self.save_file(self.text_area2, "Save File 2")

    def save_file(self, text_area, message):
        file_path = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("Binary files", "*.bin"), ("All files", "*.*")])
        if file_path:
            content = text_area.get("1.0", tk.END).strip().split("\n")
            hex_data = ''.join(''.join(line.split()[1:]) for line in content)
            bin_data = binascii.unhexlify(hex_data.replace(' ', ''))
            with open(file_path, 'wb') as file:
                file.write(bin_data)
            messagebox.showinfo(message, f"{message} saved successfully!")

    def show_files(self, text_area, canvas, file_content):
        text_area.delete(1.0, tk.END)
        hex_data = binascii.hexlify(file_content).decode('utf-8')

        length = len(hex_data)
        bytes_per_line = 32

        for i in range(0, length, bytes_per_line*2):
            addr = f"{i//2:08X}: "
            chunk = hex_data[i:i+bytes_per_line*2]
            self.insert_line(text_area, addr, chunk, chunk)

        self.update_minimap(canvas, text_area)

    def compare_files(self):
        if self.file1_content is None or self.file2_content is None:
            messagebox.showwarning("Warning", "Please load both files first.")
            return

        self.text_area1.delete(1.0, tk.END)
        self.text_area2.delete(1.0, tk.END)

        hex1 = binascii.hexlify(self.file1_content).decode('utf-8')
        hex2 = binascii.hexlify(self.file2_content).decode('utf-8')

        length = max(len(hex1), len(hex2))
        bytes_per_line = 32

        for i in range(0, length, bytes_per_line*2):
            addr = f"{i//2:08X}: "
            chunk1 = hex1[i:i+bytes_per_line*2]
            chunk2 = hex2[i:i+bytes_per_line*2]

            self.insert_line(self.text_area1, addr, chunk1, chunk2)
            self.insert_line(self.text_area2, addr, chunk2, chunk1)

        self.text_area1.tag_config('diff', foreground='red')
        self.text_area2.tag_config('diff', foreground='red')

        # Enable the Next and Back buttons
        self.btn_next.config(state=tk.NORMAL)
        self.btn_back.config(state=tk.NORMAL)
        self.btn_find.config(state=tk.NORMAL)

        self.update_minimap(self.canvas1, self.text_area1)
        self.update_minimap(self.canvas2, self.text_area2)

    def insert_line(self, text_area, addr, chunk, compare_chunk):
        text_area.insert(tk.END, addr)
        for j in range(0, len(chunk), 2):
            byte = chunk[j:j+2]
            compare_byte = compare_chunk[j:j+2] if j < len(compare_chunk) else None
            if byte != compare_byte:
                text_area.insert(tk.END, byte + ' ', 'diff')
            else:
                text_area.insert(tk.END, byte + ' ')
        text_area.insert(tk.END, '\n')

    def find_text(self):
        self.search_term = simpledialog.askstring("Find", "Enter hex string to find:")
        if self.search_term:
            self.search_start_pos = '1.0'
            self.search_results1.clear()
            self.search_results2.clear()
            self.text_area1.tag_remove('found', '1.0', tk.END)
            self.text_area2.tag_remove('found', '1.0', tk.END)
            self.text_area1.tag_remove('current_found', '1.0', tk.END)
            self.text_area2.tag_remove('current_found', '1.0', tk.END)
            self.highlight_all_occurrences(self.text_area1, self.search_results1)
            self.highlight_all_occurrences(self.text_area2, self.search_results2)
            self.current_result = -1
            self.find_next()
            self.text_area1.yview_moveto(0)
            self.text_area2.yview_moveto(0)

    def highlight_all_occurrences(self, text_area, results):
        pos = '1.0'
        while True:
            pos = text_area.search(self.search_term, pos, tk.END)
            if not pos:
                break
            end_pos = f"{pos}+{len(self.search_term)}c"
            text_area.tag_add('found', pos, end_pos)
            text_area.tag_config('found', background='blue')
            results.append(pos)
            pos = end_pos
        self.update_minimap(self.canvas1, self.text_area1)
        self.update_minimap(self.canvas2, self.text_area2)

    def find_next(self):
        total_results1 = len(self.search_results1)
        total_results2 = len(self.search_results2)
        total_results = total_results1 + total_results2

        if total_results == 0:
            messagebox.showinfo("Find", "No occurrences found.")
            return

        self.current_result += 1
        if self.current_result >= total_results:
            self.current_result = 0
        if self.current_result < total_results1:
            pos1 = self.search_results1[self.current_result]
            self.highlight_and_scroll(pos1, None)
        else:
            pos2 = self.search_results2[self.current_result - total_results1]
            self.highlight_and_scroll(None, pos2)

    def find_previous(self):
        total_results1 = len(self.search_results1)
        total_results2 = len(self.search_results2)
        total_results = total_results1 + total_results2

        if total_results == 0:
            messagebox.showinfo("Find", "No occurrences found.")
            return

        self.current_result -= 1
        if self.current_result < 0:
            self.current_result = total_results - 1

        if self.current_result < total_results1:
            pos1 = self.search_results1[self.current_result]
            self.highlight_and_scroll(pos1, None)
        else:
            pos2 = self.search_results2[self.current_result - total_results1]
            self.highlight_and_scroll(None, pos2)

    def highlight_and_scroll(self, pos1, pos2):
        if pos1:
            self.highlight_and_scroll_area(self.text_area1, pos1, self.text_area2)
        if pos2:
            self.highlight_and_scroll_area(self.text_area2, pos2, self.text_area1)

    def highlight_and_scroll_area(self, text_area, pos, other_text_area):
        text_area.tag_remove('current_found', '1.0', tk.END)
        end_pos = f"{pos}+{len(self.search_term)}c"
        text_area.tag_add('current_found', pos, end_pos)
        text_area.tag_config('current_found', background='yellow')
        text_area.mark_set("insert", pos)
        text_area.see(pos)

        # pos 위치로 이동
        line_num = int(pos.split('.')[0])
        total_lines = int(text_area.index('end-1c').split('.')[0])
        yview_percent = (line_num - 1) / total_lines
        text_area.yview_moveto(yview_percent)
        other_text_area.yview_moveto(yview_percent)
        self.update_minimap_scrollbar(self.canvas1, self.text_area1)
        self.update_minimap_scrollbar(self.canvas2, self.text_area2)

    def update_minimap(self, canvas, text_area):
        canvas.delete("all")
        text = text_area.get("1.0", tk.END)
        lines = text.split('\n')
        
        # 텍스트 위젯의 총 높이와 라인의 수를 이용하여 line_height 계산
        total_lines = len(lines)
        text_widget_height = text_area.winfo_height()
        line_height = text_widget_height / total_lines if total_lines > 0 else 1

        i = 0
        while i < total_lines:
            line = lines[i]
            y = i * line_height
            for j in range(0, len(line), 3):  # 2자리 Hex + 공백으로 이루어져 있음
                pos = f"{i + 1}.{j + 10}"  # 10은 주소와 공백을 건너뛴 offset
                tags = text_area.tag_names(pos)
                if 'found' in tags:
                    line_color = 'blue'
                    canvas.create_line(0, y, 100, y, fill=line_color, width=1)
                    break  # 파란색이 우선
                elif 'diff' in tags:
                    line_color = 'red'
                    canvas.create_line(0, y, 100, y, fill=line_color, width=1)
                    break
            i += 1
        
        canvas.config(scrollregion=canvas.bbox("all"))
        self.update_minimap_scrollbar(canvas, text_area)

    def update_minimap_scrollbar(self, canvas, text_area):
        canvas.delete("scrollbar")
        start, end = text_area.yview()
        canvas_height = int(canvas.winfo_height())
        #print(f"start: {start}, end: {end}, canvas_height: {canvas_height}")
        rect_start = start * canvas_height
        rect_end = end * canvas_height
        # 점선으로 테두리를 설정
        canvas.create_rectangle(0, rect_start, 100, rect_end, outline='black', width=1, dash=(2, 4), tag="scrollbar")

    def onResizeWindow(self, event):
        if self.resize_after_id is not None:
            self.root.after_cancel(self.resize_after_id)
        self.resize_after_id = self.root.after(10, self.on_resize)  # 200ms 후에 on_resize 호출

    def on_resize(self):
        self.update_minimap(self.canvas1, self.text_area1)
        self.update_minimap(self.canvas2, self.text_area2)
    

if __name__ == "__main__":
    root = tk.Tk()
    app = HexDiffApp(root)
    root.mainloop()
