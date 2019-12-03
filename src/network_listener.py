import pyshark

capture = pyshark.LiveCapture(interface='lo0', bpf_filter='tcp port 9001')
capture.set_debug()
for packet in capture.sniff_continuously():
    print('Just arrived:', packet)
    packet_capture = [packet.ip.src, packet.ip.dst, packet.ip.len, packet.tcp.time_delta, packet.tcp.srcport, packet.tcp.dstport]
    print(packet_capture)