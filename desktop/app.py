from tkinter import filedialog
from tkinter import *
import os
import stat
import threading
import time
from api import APIClient
# import grp, pwd
from datetime import datetime


class StatCollector:
    STAT_ATTRIBUTES = (
        {
            'name': 'st_mode',
            'label': 'File permissions',
            'resolver': 'resolve_mode',
            'key': 'mode'
        },
        {
            'name': 'st_nlink',
            'label': 'Number of hard links',
            'resolver': 'resolve_raw',
            'key': 'nlink'
        },
        {
            'name': 'st_uid',
            'label': 'File owner User',
            'resolver': 'resolve_user',
            'key': 'user'
        },
        {
            'name': 'st_gid',
            'label': 'File owner Group',
            'resolver': 'resolve_group',
            'key': 'group'
        },
        {
            'name': 'st_size',
            'label': 'Size of file',
            'resolver': 'resolve_bytes',
            'key': 'size'
        },
        {
            'name': 'st_mtime',
            'label': 'Time of most recent content modification',
            'resolver': 'resolve_datetime',
            'key': 'mtime'
        },
        {
            'name': 'st_ctime',
            'label': 'Time of most recent metadata change',
            'resolver': 'resolve_datetime',
            'key': 'ctime'
        },
        {
            'name': 'st_flags',
            'label': 'User defined flags for file',
            'resolver': 'resolve_raw',
            'key': 'flags'
        }
    )

    PERMISSIONS_MASKS = (
        {
            'mask': stat.S_IRUSR,
            'description': 'owner has read permission'
        },
        {
            'mask': stat.S_IWUSR,
            'description': 'owner has write permission'
        },
        {
            'mask': stat.S_IXUSR,
            'description': 'owner has execute permission'
        },
        {
            'mask': stat.S_IRGRP,
            'description': 'group has read permission'
        },
        {
            'mask': stat.S_IWGRP,
            'description': 'group has write permission'
        },
        {
            'mask': stat.S_IXGRP,
            'description': 'group has execute permission'
        },
        {
            'mask': stat.S_IROTH,
            'description': 'others have read permission'
        },
        {
            'mask': stat.S_IWOTH,
            'description': 'others have write permission'
        },
        {
            'mask': stat.S_IXOTH,
            'description': 'others have execute permission'
        }
    )

    def extract_data(self, file_path):
        if os.path.exists(file_path):
            return self.resolve_stats(os.stat(file_path))
        else:
            return False

    def resolve_stats(self, stats):
        resolved_stats = dict()
        for attr in self.STAT_ATTRIBUTES:
            attr_val = getattr(stats, attr.get('name'), None)
            if attr_val is not None:
                resolved_stats[attr.get('key')] = getattr(self, attr.get('resolver'))(attr_val)
        return resolved_stats

    @staticmethod
    def resolve_datetime(val):
        return datetime.fromtimestamp(float(val)).strftime("%m.%d.%Y %I:%M:%S")

    @staticmethod
    def resolve_user(val):
        try:
            username = pwd.getpwuid(int(val)).pw_name
            return f"{username} (ID: {val})"
        except KeyError:
            return 'Unknown User'
        except NameError:
            return 'Unable to receive User'

    @staticmethod
    def resolve_group(val):
        try:
            group_name = grp.getgrgid(int(val)).gr_name
            return f"{group_name} (ID: {val})"
        except KeyError:
            return 'Unknown Group'
        except NameError:
            return 'Unable to receive User'

    @staticmethod
    def resolve_bytes(val):
        return val

    def resolve_mode(self, val):
        result = list()
        for permission in self.PERMISSIONS_MASKS:
            if int(val) & permission.get('mask'):
                result.append(permission.get('description'))
        return ", ".join(result)

    @staticmethod
    def resolve_raw(val):
        return val


class GUIApplication:
    REPORT_PERIOD = ['Days', 'Hours']

    def __init__(self, width=700, height=350, title='File monitor'):
        self.app = Tk()
        self.app.title(title)
        self.app.geometry(f'{width}x{height}')
        self.app.resizable(False, False)
        self.create_gui_entries()
        self.configure_gui_grid()

    def create_gui_entries(self):
        self.file_list = Listbox(
            self.app,
            width=82,
            height=20,
            selectmode=EXTENDED)
        self.file_scrollbar_y = Scrollbar(self.app, orient=VERTICAL)
        self.file_scrollbar_x = Scrollbar(self.app, orient=HORIZONTAL)
        self.file_list.config(yscrollcommand=self.file_scrollbar_y.set, xscrollcommand=self.file_scrollbar_x.set)
        self.file_scrollbar_x.config(command=self.file_list.xview)
        self.file_scrollbar_y.config(command=self.file_list.yview)

        self.add_file_btn = Button(self.app, text='Select file', width=20)
        self.add_dir_btn = Button(self.app, text='Select directory', width=20)
        self.remove_btn = Button(self.app, text='Remove file', width=20)

        self.report_period_type = StringVar(self.app)
        self.report_period_type.set(self.REPORT_PERIOD[0])
        self.report_period_val = StringVar(self.app)
        self.report_period_val.set('1')

        self.reports_label = Label(self.app, text='Reports', font='Arial 20')
        self.report_period_type_select = OptionMenu(
            self.app, self.report_period_type, *self.REPORT_PERIOD)
        self.report_period_val_spinbox = Spinbox(
            self.app,
            textvariable=self.report_period_val,
            from_=1,
            to=60,
            wrap=True,
            width=7,
            state='readonly')
        self.text_report_btn = Button(self.app, text='Text report', width=20)
        self.html_report_btn = Button(self.app, text='HTML report', width=20)

    def configure_gui_grid(self):
        self.file_scrollbar_y.grid(row=0, column=5, rowspan=7, sticky=N+S)
        self.file_scrollbar_x.grid(row=7, column=3, padx=(15, 0), sticky=E+W)
        self.file_list.grid(row=0, column=3, rowspan=7, pady=(5, 0), padx=(15, 0), sticky=N+S+E+W)

        self.add_file_btn.grid(row=0, column=0, columnspan=2, padx=5, pady=(20, 0))
        self.add_dir_btn.grid(row=1, column=0, columnspan=2, padx=5)
        self.remove_btn.grid(row=2, column=0, columnspan=2, padx=5)

        self.reports_label.grid(row=3, column=0, columnspan=2, pady=(80, 0))
        self.report_period_type_select.grid(row=4, column=0, padx=5)
        self.report_period_val_spinbox.grid(row=4, column=1, padx=5)
        self.text_report_btn.grid(row=5, column=0, columnspan=2)
        self.html_report_btn.grid(row=6, column=0, columnspan=2)

    def get_selected_report_period(self):
        period = dict()
        period[self.report_period_type.get().lower()] = int(self.report_period_val.get())
        return period

    def reset_file_list(self, qs):
        self.file_list.delete(0, END)
        for file in reversed(qs):
            self.file_list.insert(0, file.get('file_path'))

    def get_selected_files(self):
        return list(self.file_list.curselection())

    def run(self):
        self.app.mainloop()


class ReportBuilder:
    HTML_BASE_HEADER = '''<!DOCTYPE HTML>
                          <html>
                           <head>
                            <meta charset="utf-8">
                            <title>Report</title>
                            <style type="text/css">
                                * {{
                                    font-family: sans-serif;
                                }}
                                .change-table {{
                                    border-collapse: collapse;
                                    margin: 25px 0;
                                    font-size: 0.9em;
                                    min-width: 400px;
                                    border-radius: 5px 5px 0 0;
                                    overflow: hidden;
                                    box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
                                    margin-right: auto;
                                    margin-left: auto;
                                    width: 70%;
                                    font-size: 20px;
                                }}
                                .change-table thead tr {{
                                    background-color: #009879;
                                    color: #ffffff;
                                    text-align: left;
                                    font-weight: bold;
                                }}
                                .change-table th,
                                .change-table td {{
                                    padding: 12px 15px;
                                    text-align: center;
                                }}
                                .change-table tbody tr {{
                                    border-bottom: 1px solid #dddddd;
                                }}
                                .change-table tbody tr:nth-of-type(even) {{
                                    background-color: #f3f3f3;
                                }}
                                .change-table tbody tr:last-of-type {{
                                    border-bottom: 2px solid #009879;
                                }}
                                .file-separator {{
                                    border: 0;
                                    border-bottom: 5px solid #009879;
                                    margin-top: 15px;
                                    margin-bottom: 10px;
                                }}
                                .file-info {{
                                    font-size: 22px;
                                    margin-left: 30px;
                                }}
                                .header {{
                                    text-align: center;
                                    font-size: 20px;
                                }}
                                .change-header {{
                                    width: 70%;
                                    margin-left: auto;
                                    margin-right: auto;
                                    text-align: center;
                                    font-size: 23px
                                }}
                            </style>
                           </head>
                           <body>
                            <div class="header">
                             <h1>Report from {0}</h1>
                             <p>Files in tracking: <b>{1}</b></p>
                            </div>
                       '''
    HTML_BASE_FOOTER = ''' </body>
                          </html>
                       '''
    HTML_FILE_INFORMATION = '''<hr class="file-separator"/>
                               <div class="file-info">
                                <p>File path: <b>{0}</b></p>
                                <p>Current file status: <b>{1}</b></p>
                                <p>Latest stat record datetime: <b>{2}</b></p>
                               </div>
                            '''

    HTML_TABLE_HEADER = '''<p class="change-header">Changes made between <b>{0}</b> and <b>{1}</b></p>
                           <table class="change-table" border="2">
                           <thead>
                            <tr><th>What changed</th><th>Previous value</th><th>Current value</th></tr>
                           </thead>
                           <tbody>
                        '''
    HTML_TABLE_ROW = '<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>'
    HTML_CLOSE_TABLE = '</tbody></table>'

    TXT_BASE_HEADER = '''Report from {0}\n
Files in tracking: {1}
'''
    TXT_FILE_INFORMATION = '''=======================================\n
File path: {0}\n
Current file status: {1}\n
Latest stat record datetime: {2}
'''
    TXT_TABLE_HEADER = 'Change detected in period of time: {0} - {1}'
    TXT_TABLE_ROW = "What changed: '{0}', previous value: '{1}', current value: '{2}'"

    @staticmethod
    def get_report_qs(period):
        api_cli = APIClient()
        return api_cli.get_report(period)

    def generate_report(self, period,
                        header_template,
                        file_information_template,
                        table_header_template,
                        table_row_template,
                        close_table_template='',
                        footer_template=''):
        report_qs = self.get_report_qs(period)
        report = list()

        # Append header
        report.append(
            header_template.format(
                report_qs.get('start_datetime'),
                len(report_qs.get('diffs'))
            )
        )

        for file_diff in report_qs.get('diffs'):
            file = file_diff.get('file')
            diff = file_diff.get('diff')

            # Append information about file
            report.append(
                file_information_template.format(
                    file.get('file_path'),
                    file.get('status'),
                    file_diff.get('latest_stat')
                )
            )

            for changes in diff:
                report.append(
                    table_header_template.format(
                        changes.get('prev_date'),
                        changes.get('current_date')
                    )
                )

                for row in changes.get('changes'):
                    report.append(
                        table_row_template.format(
                            row.get('attr_label'),
                            row.get('prev_val'),
                            row.get('current_val')
                        )
                    )

                report.append(close_table_template)
        report.append(footer_template)
        return "\n".join(report)

    def generate_html_report(self, period):
        return self.generate_report(
            period,
            self.HTML_BASE_HEADER,
            self.HTML_FILE_INFORMATION,
            self.HTML_TABLE_HEADER,
            self.HTML_TABLE_ROW,
            self.HTML_CLOSE_TABLE,
            self.HTML_BASE_FOOTER
        )

    def generate_txt_report(self, period):
        return self.generate_report(
            period,
            self.TXT_BASE_HEADER,
            self.TXT_FILE_INFORMATION,
            self.TXT_TABLE_HEADER,
            self.TXT_TABLE_ROW
        )


class BackgroundStatAnalyzer:
    def __init__(self, interval=60):
        self.interval = interval

        self.thread = threading.Thread(target=self.run_thread, args=())
        self.thread.daemon = True
        self.thread.start()

    def run_thread(self):
        while True:
            api_cli = APIClient()
            stat_collector = StatCollector()
            current_list = api_cli.get_active_files()
            for file in current_list:
                stat_data = stat_collector.extract_data(file.get('file_path'))
                if file.get('status') != 'Unavailable' or stat_data:
                    api_cli.add_file_stats(
                        file.get('id'),
                        stat_data
                    )
            time.sleep(self.interval)


class Application:
    PATH_TO_REPORTS = 'reports'

    def __init__(self, interval=30):
        self.interval = interval
        self.gui_app = GUIApplication()
        self.api_cli = APIClient()
        self.stat_collector = StatCollector()
        self.current_list = self.api_cli.get_active_files()
        self.bind_gui_actions()

        self.stats_thread = None

    def extract_files(self, directory_path):
        files = []
        for file in os.listdir(directory_path):
            cur_path = f'{directory_path}/{file}'
            if os.path.isfile(os.path.join(directory_path, file)):
                files.append(cur_path)
            else:
                files += self.extract_files(cur_path)

        return files

    def load_directory(self, *args):
        directory_path = filedialog.askdirectory(title='Select directory')

        if directory_path:
            files = self.extract_files(directory_path)
            for file_path in files:
                file = self.api_cli.add_file(file_path)
                self.api_cli.add_file_stats(
                    file.get('id'),
                    self.stat_collector.extract_data(file_path)
                )
            self.update_current_list()
            self.reset_file_list()

    def load_file(self, *args):
        file_path = filedialog.askopenfilename(title='Select file')

        if file_path:
            file = self.api_cli.add_file(file_path)
            self.api_cli.add_file_stats(
                file.get('id'),
                self.stat_collector.extract_data(file_path)
            )
            self.update_current_list()
            self.reset_file_list()

    def removefile(self, *args):
        selection = self.gui_app.get_selected_files()
        selection.reverse()

        for i in selection:
            self.gui_app.file_list.delete(i)
            rec = self.current_list.pop(i)
            self.api_cli.change_file_status(rec.get('id'), 'Inactive')

    def generate_txt_report(self, *args):
        builder = ReportBuilder()
        report = builder.generate_txt_report(self.gui_app.get_selected_report_period())

        self.create_report_file(report, 'txt')

    def generate_html_report(self, *args):
        builder = ReportBuilder()
        report = builder.generate_html_report(self.gui_app.get_selected_report_period())

        self.create_report_file(report, 'html')

    def create_report_file(self, report, report_type):
        if not os.path.exists(self.PATH_TO_REPORTS):
            os.makedirs(self.PATH_TO_REPORTS)

        i = 0
        while True:
            try:
                file_num = f'({i})' if i != 0 else ''
                f = open(
                    f'{self.PATH_TO_REPORTS}/report{file_num}.{report_type}', 'x')
                break
            except FileExistsError:
                i += 1

        f.write(report)
        f.close()

    def bind_gui_actions(self):
        self.gui_app.add_file_btn.bind('<ButtonRelease-1>', self.load_file)
        self.gui_app.add_dir_btn.bind('<ButtonRelease-1>', self.load_directory)
        self.gui_app.remove_btn.bind('<ButtonRelease-1>', self.removefile)
        self.gui_app.text_report_btn.bind(
            '<ButtonRelease-1>',
            self.generate_txt_report)
        self.gui_app.html_report_btn.bind(
            '<ButtonRelease-1>',
            self.generate_html_report)

    def update_current_list(self):
        self.current_list = self.api_cli.get_active_files()

    def reset_file_list(self):
        self.gui_app.reset_file_list(self.current_list)

    def run_background_tasks(self):
        self.stats_thread = BackgroundStatAnalyzer(self.interval)

    def run_app(self):
        self.reset_file_list()
        self.run_background_tasks()
        self.gui_app.run()


app = Application()
app.run_app()
