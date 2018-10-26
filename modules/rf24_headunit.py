import bens_rf24
 
class rf24_headunit():
  def __init__(self, radio, rxpipe, addr=0xE7E7E7E7E7):
    self.radio = radio
    self.rxpipe = rxpipe
    self.addr = addr
    self.radio.set_rx_pipeline(chan=self.rxpipe, enable=1, addr=self.addr)
    
  def display(self, payload):
    as_bytes = [ord('D')] + map(lambda x: ord(x), list(str(payload)))
    self.radio.set_tx_pipeline(self.addr)
    self.radio.set_tx_mode()
    self.radio.activate()
    return self.radio.w_tx_payload(as_bytes)

  def led(self, color):
    as_bytes = [ord('L'), ord(color[0].upper())]
    self.radio.set_tx_pipeline(self.addr)
    self.radio.set_tx_mode()
    self.radio.activate()
    return self.radio.w_tx_payload(as_bytes)

##########

