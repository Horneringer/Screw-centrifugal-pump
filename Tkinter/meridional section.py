from tkinter import *

root = Tk()
root.title('Графические примитивы')

canv = Canvas(root, width=1920, height=1080, bg="white", cursor="pencil")
# canv.create_rectangle(20, 150, 300, 450, fill="green", outline="black")
# canv.create_polygon([20, 150], [160, 30], [300, 150], fill="blue", outline="blue")
# canv.create_polygon([300, 450], [300, 300], [400, 300], [400, 375], [480, 375], [480, 450], fill="red", outline="black")
# canv.create_oval(400, 10, 480, 80, fill="yellow", outline="yellow")
# canv.create_line(300, 150, 300, 30, width=2, fill="black")
# canv.create_line(300, 30, 270, 0, width=2, fill="black")
# canv.create_line(300, 30, 330, 0, width=2, fill="black")
# canv.create_arc([20, 20], [100, 100], start=220, extent=180, style=ARC, outline="darkred", width=2)
# canv.create_text(20, 470, text="Домик в деревне", font="Verdana 12", anchor="w", justify=CENTER, fill="darkblue")

canv.create_line(500, 500, 530, 500, width=2)
canv.create_arc([550, 500], [500, 450], start=270, extent=90, style=ARC, outline="black", width=2)
canv.create_line(550, 400, 550, 480, width=2)
canv.create_line(550, 400, 580, 400, width=2)
canv.create_line(580, 400, 580, 500, width=2)
canv.create_arc([580, 550], [490, 450], start=270, extent=90, style=ARC, outline="black", width=2)
canv.create_line(540, 550, 500, 550, width=2)
canv.create_line(500, 500, 500, 550, width=2)

canv.pack()

root.mainloop()
