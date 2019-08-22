import bens_rf24
 
class rf24_headunit():
  def __init__(self, radio, addr=0xE7E7E7E7E7):
    self.radio = radio
    self.addr = addr

class rf24_headunit():
  def __init__(self, radio, addr=0xE7E7E7E7E7):
    self.radio = radio
    self.addr = addr

    # Framebuffer is eight rows, each row representing
    # 16 bits of width. Two color channels.
    self.fb = { 'R': [0,0,0,0,0,0,0,0],
                'G': [0,0,0,0,0,0,0,0] }

  # Break the 16-bit framebuffer rows into 8-bit words
  def fbreducer(c, i):
    c.extend([i>>8, i & 0xFF]
    return c

  def display(self, payload):
    self.radio.set_tx_pipeline(self.addr)
    rchan = [ord('D'), ord('R')] + reduce(self.fbreducer, self.fb['R'], [])
    gchan = [ord('D'), ord('R')] + reduce(self.fbreducer, self.fb['G'], [])
    return self.radio.w_tx_payload(rchan) and self.radio.w_tx_payload(gchan)

##########
