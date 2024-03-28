import dearpygui.dearpygui as dpg

VERSION_STR = '0.1'
MAIN_WINDOW_NAME = 'Indevendent v ' + VERSION_STR

dpg.create_context()

with dpg.window(tag=MAIN_WINDOW_NAME):
    dpg.add_listbox(pos=(0,0), items=['test1',2])

dpg.create_viewport(title=MAIN_WINDOW_NAME, width=600, height=200)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window(MAIN_WINDOW_NAME, True)

# below replaces, start_dearpygui()
while dpg.is_dearpygui_running():
    # insert here any code you would like to run in the render loop
    # you can manually stop by using stop_dearpygui()
    dpg.render_dearpygui_frame()

dpg.destroy_context()