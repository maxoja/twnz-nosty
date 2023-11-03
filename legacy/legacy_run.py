# ports = returnAllPorts()
#     port = []
#
#     if len(ports) == 1:
#         port = [int(ports[0][1])]
#     else:
#         port = []
#
#     if not port:
#         port_selection_app = PortSelectionGUI(ports, port)
#         port_selection_app.show()
#         print('exec')
#         app.exec_()
#         print('exiting')
#         app.exit(0)
#         print('exited')
#
#     if not port:
#         print('no port selected after port gui')
#         exit(1)
#
#     # port = input("enter port: ")
#     api = phoenix.Api(int(port[0]))
#
#     print('starting api')
#
#     while api.working():
#         occasional_log(api)
#
#         if not api.empty():
#             msg = api.get_message()
#             json_msg = json.loads(msg)
#
#             if json_msg["type"] == phoenix.Type.packet_send.value:
#                 # handle_send(json_msg["packet"])
#                 pass
#             elif json_msg["type"] == phoenix.Type.packet_recv.value:
#                 handle_recv(api, json_msg["packet"])
#                 pass
#             else:
#                 # unhandled msg type
#                 pass
#         else:
#             sleep(twnzlib.config.API_INTERVAL)
#     api.close()