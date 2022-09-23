# coding=utf-8
#   _________________ .________________________
#  /   _____/\_____  \|   \______   \_   _____/
#  \_____  \  /  ____/|   ||     ___/|    __)
#  /        \/       \|   ||    |    |     \
# /_______  /\_______ \___||____|    \___  /
#         \/         \/                  \/
# ________                .__                     __                 __
# \_____  \_______   ____ |  |__   ____   _______/  |_____________ _/  |_  ___________
#  /   |   \_  __ \_/ ___\|  |  \_/ __ \ /  ___/\   __\_  __ \__  \\   __\/  _ \_  __ \
# /    |    \  | \/\  \___|   Y  \  ___/ \___ \  |  |  |  | \// __ \|  | (  <_> )  | \/
# \_______  /__|    \___  >___|  /\___  >____  > |__|  |__|  (____  /__|  \____/|__|
#         \/            \/     \/     \/     \/                   \/
#
#
#  Copyright (C) 2014-2022 CS GROUP – France, https://www.csgroup.eu
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# author : Esquis Benjamin for CSGroup
#
import Tkinter as tk
import ttk
import tkMessageBox
import tkFileDialog
import xmlrpclib
import os

host = "localhost"
port = 8100
host_file = None

new_env = os.environ.copy()
if "IDPORCH_PORT" in new_env:
    port = int(new_env["IDPORCH_PORT"])

connection_string = 'http://' + host + ':' + str(port)

s = xmlrpclib.ServerProxy(connection_string)


# try:
#    alive = s.is_alive()
# except:
#    print "%s is not available." % connection_string
#    sys.exit(0)


class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master, width=800, height=600)
        self.hsb = tk.Scrollbar(self.statusboard, orient=tk.VERTICAL, command=self.canvas.yview)
        self.statuslist = tk.Frame(self.canvas, width=800, height=500)
        self.canvas = tk.Canvas(self.statusboard, width=800, height=500)
        self.statusboard = tk.Frame(self.statusframe, width=800, height=500)
        self.tasktext = None
        self.poolidtext = None
        self.statusheader = tk.Frame(self.statusframe, width=800, height=24, relief=tk.RAISED, bd=1)
        self.statusframe = ttk.Labelframe(self, width=800, height=500, text='Task status')
        self.refresh_label = tk.Label(self.refreshbar, text="Seconds")
        self.refresh_entry = ttk.Entry(self.refreshbar, width=3, textvariable=self.refresh_time)
        self.refresh_time = tk.StringVar()
        self.refresh_button = tk.Checkbutton(self.refreshbar, text="Auto", variable=self.do_refresh)
        self.do_refresh = tk.IntVar()
        self.refreshbar = ttk.Labelframe(self.topbar, width=160, height=60, text='Refresh')
        self.statelabel = tk.Label(self.statebar, textvariable=self.statetext, relief=tk.SUNKEN, bd=4, width=14,
                                   bg=self.orch_STOP)
        self.statetext = tk.StringVar()
        self.statebar = ttk.Labelframe(self.topbar, width=140, height=60, text='State')
        self.statusButton = tk.Button(self.buttonbar, text='Status',
                                      command=self.state)
        self.resumeButton = tk.Button(self.buttonbar, text='Resume',
                                      command=self.resume)
        self.pauseButton = tk.Button(self.buttonbar, text='Pause',
                                     command=self.pause)
        self.stopButton = tk.Button(self.buttonbar, text='Stop',
                                    command=self.stop)
        self.startButton = tk.Button(self.buttonbar, text='Start',
                                     command=self.start)
        self.buttonbar = ttk.Labelframe(self.topbar, width=500, height=60, text='Command')
        self.topbar = tk.Frame(self, width=800, height=52)
        self.orch_STOP = "#f33"
        self.orch_RUNNING = "#3f3"
        self.orch_IDLE = "#35f"
        self.sizes = [3, 31, 9, 5, 13, 5, 7, 15, 5]
        self.headers = ["Pool", "Name", "Pid", "id", "Begin", "T", "RAM", "Status", "Code"]
        self.pack_propagate(0)
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        # Parameters
        # TopBar
        self.topbar.pack_propagate(0)
        self.topbar.pack(side=tk.TOP, padx=3, pady=3)
        # Buttons
        self.buttonbar.pack_propagate(0)
        self.buttonbar.pack(side=tk.LEFT)
        self.startButton.pack(side=tk.LEFT, fill='x', expand=1, padx=3)
        self.stopButton.pack(side=tk.LEFT, fill='x', expand=1, padx=3)
        self.pauseButton.pack(side=tk.LEFT, fill='x', expand=1, padx=3)
        self.resumeButton.pack(side=tk.LEFT, fill='x', expand=1, padx=3)
        self.statusButton.pack(side=tk.LEFT, fill='x', expand=1, padx=3)
        # Orchestrator status
        self.statebar.pack_propagate(0)
        self.statebar.pack(side=tk.LEFT)
        self.statetext.set('STOPPED')
        self.statelabel.pack(fill='x', expand=1, padx=10)
        # Refresh options
        self.refreshbar.pack_propagate(0)
        self.refreshbar.pack(side=tk.LEFT)
        self.do_refresh.set(1)
        self.refresh_button.pack(side=tk.LEFT)
        self.refresh_time.set("5")
        self.refresh_entry.pack(side=tk.LEFT)
        self.refresh_label.pack(side=tk.LEFT)

        # task status panel
        self.statusframe.pack_propagate(0)
        self.statusframe.pack(side=tk.TOP, padx=3)
        # Task status header
        self.statusheader.pack_propagate(0)
        self.statusheader.pack(side=tk.TOP)
        for f in range(len(self.headers)):
            self.poolidtext.pack(side=tk.LEFT)
            self.poolidtext = tk.Label(self.statusheader, text=self.headers[f], relief=tk.RAISED, height=24, bd=1,
                                       width=self.sizes[f])
        # List of task status
        self.statusboard.pack_propagate(0)
        self.statusboard.pack()
        self.statusboard.grid_rowconfigure(0, weight=1)
        self.statusboard.grid_columnconfigure(0, weight=1)
        self.canvas.grid(row=0, column=0, sticky=tk.N + tk.W + tk.E + tk.S)
        self.hsb.grid(row=0, column=1, sticky=tk.N + tk.S)
        self.canvas['yscrollcommand'] = self.hsb.set
        self.statuslist.pack()
        self.canvas.create_window(0, 0, window=self.statuslist, anchor=tk.NW)
        self.statuslist.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.after(5000, self.state)

    def start(self):
        if self.statetext.get() == "RUNNING":
            tkMessageBox.showinfo("Info", "A tasktable is already running !!!!")
        else:
            options = {'defaultextension': '.xml', 'filetypes': [('xml files', '.xml')]}
            filename = tkFileDialog.askopenfilename(**options)
            param = {"filename": filename}
            s.start(param)

    def stop(self):
        result = s.stop({})
        self.statetext.set("IDLE")

    def pause(self):
        s.pause({})

    def resume(self):
        s.resume({})

    def status(self):
        for child in self.statuslist.winfo_children():
            child.destroy()
        self.statuslist.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        statuslist = s.status({})
        oldbg = "#ddd"
        nextbg = "#fff"
        errbg = "#fdd"
        sucbg = "#dfd"
        abobg = "#ddf"
        index = 0
        for p in range(len(statuslist)):
            for t in range(len(statuslist[p])):
                task_status = str(statuslist[p][t][7])
                tmpbg = oldbg
                if task_status == "FINISHED":
                    tmpbg = sucbg
                if task_status == "ERROR":
                    tmpbg = errbg
                if task_status == "ABORTED":
                    tmpbg = abobg
                for e in range(len(self.headers)):
                    self.tasktext = tk.Label(self.statuslist, text=str(statuslist[p][t][e]), relief=tk.FLAT,
                                             width=self.sizes[e], padx=1, bg=tmpbg)
                    self.tasktext.grid(column=e, row=index)
                index += 1
                tmpbg = str(oldbg)
                oldbg = nextbg
                nextbg = tmpbg
        self.statuslist.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def state(self):
        for child in self.statebar.winfo_children():
            child.destroy()
        try:
            alive = s.is_alive()
            is_processing = s.is_processing()
            self.status()
            if is_processing:
                self.statetext.set("RUNNING")
                self.statelabel = tk.Label(self.statebar, textvariable=self.statetext, relief=tk.SUNKEN, bd=4, width=14,
                                           bg=self.orch_RUNNING)
                self.statelabel.pack(fill='x', expand=1, padx=10)
                refresh_time = int(self.refresh_time.get())
                if refresh_time < 1:
                    tkMessageBox.showinfo("Error", "Refresh time should be at least 1 second")
                elif self.do_refresh.get() == 1:
                    self.after(int(self.refresh_time.get()) * 1000, self.state)
            else:
                self.statetext.set("IDLE")
                self.statelabel = tk.Label(self.statebar, textvariable=self.statetext, relief=tk.SUNKEN, bd=4, width=14,
                                           bg=self.orch_IDLE)
                self.statelabel.pack(fill='x', expand=1, padx=10)
                refresh_time = int(self.refresh_time.get())
                if refresh_time < 1:
                    tkMessageBox.showinfo("Error", "Refresh time should be at least 1 second")
                elif self.do_refresh.get() == 1:
                    self.after(int(self.refresh_time.get()) * 1000, self.state)
        except:
            self.statetext.set("STOPPED")
            self.statelabel = tk.Label(self.statebar, textvariable=self.statetext, relief=tk.SUNKEN, bd=4, width=14,
                                       bg=self.orch_STOP)
            self.statelabel.pack(fill='x', expand=1, padx=10)


def main():
    root = tk.Tk()
    root.minsize(800, 600)
    root.maxsize(800, 600)
    root.geometry("800x600")
    app = Application(root)
    app.master.title('Orchestrator')
    app.mainloop()


if __name__ == "__main__":
    main()
