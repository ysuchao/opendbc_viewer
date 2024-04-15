import cantools
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk


def parse_dbc(file_path, globals):
    db = cantools.database.load_file(file_path)
    # print(db)

    # 设置globals["tree"]的名称，左对齐
    file_name = file_path.split("/")[-1]
    globals["tree"].heading("#0", text=file_name, anchor=tk.W)
    globals["tree"].delete(*globals["tree"].get_children())

    # 清空globals["table"]
    globals["table"].delete(*globals["table"].get_children())

    nodes = globals["tree"].insert("", tk.END, text="Nodes")
    # 根据node.name的顺序插入
    for node in sorted(db.nodes, key=lambda x: x.name):
        globals["tree"].insert(
            nodes, tk.END, text=f"{node.name}", values=("node", node.name)
        )

    messages = globals["tree"].insert("", tk.END, text="Messages")
    for message in sorted(db.messages, key=lambda x: x.name):
        globals["tree"].insert(
            messages,
            tk.END,
            text=f"{message.name}[{message.frame_id}][0x{hex(message.frame_id)[2:].upper()}]",
            values=("message", message.name, message.frame_id),
        )

    return db


def on_tree_select(event, globals):
    item = event.widget.selection()[0]
    values = event.widget.item(item, "values")
    if not values:
        globals["table"].delete(*globals["table"].get_children())
        return
    item_type, item_value = values[0], values[1:]

    globals["table"].delete(*globals["table"].get_children())
    if item_type == "node":
        node = globals["db"].get_node_by_name(item_value[0])
        globals["table"]["columns"] = ("#1",)
        globals["table"].column("#0", width=100)
        globals["table"].column("#1", width=100)
        globals["table"].heading("#0", text="Name")
        globals["table"].heading("#1", text="Comment")
        # 显示node的名称和注释
        globals["table"].insert(
            "",
            tk.END,
            text=node.name,
            values=(node.comment,),
        )

    elif item_type == "message":
        message = globals["db"].get_message_by_name(item_value[0])
        globals["table"]["columns"] = (
            "#StartBit",
            "#Length",
            "#ByteOrder",
            "#Signed",
            "#RawInitial",
            "#Scale",
            "#Offset",
            "#Minimum",
            "#Maximum",
            "#Unit",
            # "#Multiplexer",
            # "#MultiplexerIds",
            "#Choices",
            # "#SPN",
            "#Comments",
        )
        globals["table"].column("#0", width=200)
        globals["table"].heading("#0", text="Name")
        for column in globals["table"]["columns"]:
            globals["table"].column(column, width=50)
            globals["table"].heading(column, text=column[1:])
        globals["table"].column("#Choices", width=300)
        globals["table"].column("#Comments", width=300)

        # 显示message的signals
        for signal in message.signals:
            choices = None
            if signal.choices is not None:
                choices = ", ".join(
                    [
                        f"{value}: {text}"
                        for value, text in sorted(
                            signal.choices.items(), key=lambda x: x[0]
                        )
                    ]
                )
            comments = None
            if signal.comments is not None:
                comments = ", ".join(signal.comments.values())
            globals["table"].insert(
                "",
                tk.END,
                text=signal.name,
                values=(
                    signal.start,
                    signal.length,
                    signal.byte_order,
                    signal.is_signed,
                    signal.raw_initial,
                    signal.conversion.scale,
                    signal.conversion.offset,
                    signal.minimum,
                    signal.maximum,
                    signal.unit,
                    # signal.is_multiplexer,
                    # signal.multiplexer_ids,
                    choices,
                    # signal.spn,
                    comments,
                ),
            )


def open_file_dialog(globals):
    file_path = filedialog.askopenfilename(filetypes=[("can dbc files", "*.dbc")])
    if file_path:
        globals["db"] = parse_dbc(file_path, globals)


def show_about_info():
    messagebox.showinfo("About", "Version: 1.0\nAuthor: ysuchao@126.com")


if __name__ == "__main__":
    root = tk.Tk()

    # Get screen width and height
    screen_width = root.winfo_screenwidth()
    # screen_height = root.winfo_screenheight()

    # Maximize the window
    root.attributes("-zoomed", True)

    globals = {"db": None, "tree": None, "table": None}

    panedwindow = tk.PanedWindow(root, orient=tk.HORIZONTAL)
    panedwindow.pack(fill=tk.BOTH, expand=True)

    table = ttk.Treeview(panedwindow)
    panedwindow.add(table)
    globals["table"] = table

    tree = ttk.Treeview(panedwindow)
    tree_init_width = min(320, screen_width // 6)
    panedwindow.add(tree, before=table, width=tree_init_width)
    tree.bind("<<TreeviewSelect>>", lambda event: on_tree_select(event, globals))
    globals["tree"] = tree

    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(
        label="Open", underline=0, command=lambda: open_file_dialog(globals)
    )
    filemenu.add_command(label="Exit", underline=0, command=root.quit)
    menubar.add_cascade(label="File", underline=0, menu=filemenu)

    helpmenu = tk.Menu(menubar, tearoff=0)
    helpmenu.add_command(label="About", underline=0, command=show_about_info)
    menubar.add_cascade(label="Help", underline=0, menu=helpmenu)

    root.config(menu=menubar)
    root.mainloop()
