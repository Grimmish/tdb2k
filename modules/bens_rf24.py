import spidev
import wiringpi2 as wpi
 
class bens_rf24:
  def __init__(self, addr=0xE0E0E0E0E0, debug=False):
    self.addr = addr

    self.debug = debug;
    if debug:
      print("Initializing RF24 via /dev/spidev0.0")

    self.spi = spidev.SpiDev()
    self.spi.open(0,0)

    self.ce = 6
    wpi.wiringPiSetup()
    wpi.pinMode(self.ce, wpi.GPIO.OUTPUT)
    wpi.digitalWrite(self.ce, 0)

    ##
    ## Config registers (most borrowed from Arduino RF24 lib defaults)
    ##
    # CONFIG :: Base configuration
    self.MASK_RX_DR = 1
    self.MASK_TX_DS = 1
    self.MASK_MAX_RT = 1
    self.EN_CRC = 1
    self.CRCO = 1
    self.PWR_UP = 1
    self.PRIM_RX = 1
    self.write_config()

    #### Radio params (match the Arduino lib defaults)
    self.w_register(0x01, [0b00111111])  # EN_AA :: Auto-acknowledgement (on for all pipes)
    self.w_register(0x02, [0b00000000])  # EN_RXADDR :: Enabled RX pipes (disable all)
    self.w_register(0x03, [0b00000011])  # SETUP_AW :: Address space size (5 bytes)
    self.w_register(0x04, [0b00111111])  # SETUP_RETR :: TX retry behavior (1ms delay, 15 attempts)
    self.w_register(0x05, [76])          # RF_CH :: Frequency: 2400Mhz + (n * 1Mhz)
    self.w_register(0x06, [0b00000110])  # RF_SETUP :: Data rate & power (1 MBps, max power)
    self.w_register(0x07, [0b01110000])  # STATUS :: Various event flags (clear all)
    self.w_register(0x11, [0b00000000])  # RX_PW_P0 :: >>>
    self.w_register(0x12, [0b00000000])  # RX_PW_P1 :: >>>>>
    self.w_register(0x13, [0b00000000])  # RX_PW_P2 :: >>>>>>> Expected payload sizes for each
    self.w_register(0x14, [0b00000000])  # RX_PW_P3 :: >>>>>>> RX pipe (n/a, we're dynamic)
    self.w_register(0x15, [0b00000000])  # RX_PW_P4 :: >>>>>
    self.w_register(0x16, [0b00000000])  # RX_PW_P5 :: >>>
    self.w_register(0x1C, [0b00111111])  # DYNPD :: Dynamic payload (enable for all pipes)
    self.w_register(0x1D, [0b00000100])  # FEATURE :: Fancy bits (turn on dynamic payload sizing)

    ###
    ### Other housecleaning
    ###
    # Turn off all RX pipes
    for p in range(0,5):
      self.set_rx_pipeline(chan=p, enable=0)
    # Clear all resettable status bits. Clean slate!
    self.w_register(0x07, [0b01110000])

    # Flush FIFOs
    self.flush_rx()
    self.flush_tx()

  def transfer(self, frames):
    receive = self.spi.xfer2(frames)
    if self.debug:
      print("\n>>> Sent:     " + "__".join(map(lambda x: "{0:08b}".format(x), frames)))
      print("(hex/dec):    " + "___".join(map(lambda x: "{:02X}..{:03d}".format(x,x), frames)))
      print("<<< Response: " + "__".join(map(lambda x: "{0:08b}".format(x), receive)))
      print("   (hex/dec): " + "___".join(map(lambda x: "{:02X}..{:03d}".format(x,x), receive)))
    return receive

  def flush_rx(self):
    self.transfer([0b11100010])
    return None

  def flush_tx(self):
    self.transfer([0b11100001])
    return None

  def rx_dr(self):
    return (self.getstatus()>>6) & 1

  def r_rx_payload(self):
    payload = [] 
    while not self.rx_empty():
      paylen = self.transfer([0b01100000, 0b00000000])[1]
      payload = payload + self.transfer([0b01100001] + ([0b00000000] * paylen))[1:]
      self.w_register(0x07, [1<<6])
    return payload

  def w_tx_payload(self, payload, block=True):
    self.set_tx_mode()
    self.transfer([0b10100000] + payload[:32])  # Push payload into TX buffer
    #FIXME wpi.digitalWrite(self.ce, 1)  # Come out of standby
    if not block:
      return None # Did it get there? Who cares! DON'T USE THIS.

    tx_completed = (self.getstatus()>>5) & 1 # TX_DS (data sent successfully)
    while not tx_completed: 
      tx_completed = (self.getstatus()>>5) & 1 # TX_DS (data sent successfully)
      max_rt = (self.getstatus()>>4) & 1 # Failed due to retransmit limit
      if max_rt:
        self.flush_tx() # Clear the TX_FIFO
        self.w_register(0x07, [ 1<<4 ]) # Squelch the retransmit failure
        self.set_rx_mode() # Always return to RX mode by default
        return False  # We failed

    self.w_register(0x07, [ 1<<5 ]) # Clear "TX successful" flag to reset state
    wpi.digitalWrite(self.ce, 0)  # Back to standby
    attempts = 1 + (self.r_register(0x08, 1)[0] & 0b1111)
    self.set_rx_mode() # Always return to RX mode by default
    return attempts

  def r_register(self, register, length):
    packet = [0x00 | register] + ([0] * length)
    return self.transfer(packet)[1:]

  def w_register(self, register, payload):
    packet = [0x20 | register] + payload
    return self.transfer(packet)[0]

  def write_config(self):
    return self.w_register(0x00, [self.MASK_RX_DR<<6 | self.MASK_TX_DS<<5 | self.MASK_MAX_RT<<4 | self.EN_CRC<<3 | self.CRCO<<2 | self.PWR_UP<<1 | self.PRIM_RX])

  def getstatus(self):
    return self.transfer([0])[0];
 
  def rx_empty(self):
    return self.r_register(0x17, 1)[0] & 1

  def activate(self):
    #FIXME self.w_register(0x07, [0b01110000]) # Clear all resettable status bits. Clean slate!
    wpi.digitalWrite(self.ce, 1)

  def deactivate(self):
    wpi.digitalWrite(self.ce, 0)

  def set_rx_mode(self):
    self.PRIM_RX = 1
    self.write_config()
    #FIXME wpi.digitalWrite(self.ce, 1)  # Make sure radio is active
    self.activate()

  def set_tx_mode(self):
    self.PRIM_RX = 0
    self.write_config()
    #FIXME wpi.digitalWrite(self.ce, 0)  # Stay in standby until actual xmit
    self.deactivate()  # Cycle the CE pin (apparently required)
    self.activate()

  def set_rx_pipeline(self, chan=None, enable=None, addr=None, payloadlen=None):
    if not chan >= 0 or not chan < 6:
      return False
    if enable is not None:
      # Read back the current settings & apply change for this pipe
      en_current = self.r_register(0x02, 1)[0]
      en_new = en_current | (1<<chan) if enable else en_current & ~(1<<chan)
      self.w_register(0x02, [en_new])
    if addr is not None:
      # On RX pipes 2-5, only the last byte is unique. The first 4 are always
      # shared with pipe 1
      if chan > 1:
        addr &= 0xFF
        self.w_register(0x0A + chan, [ addr ])
      else:
        self.w_register(0x0A + chan, self.to_bytes(addr & 0xFFFFFFFFFF, 5)) # Limit to 5 bytes
    if payloadlen is not None:
      self.w_register(0x11 + chan, [payloadlen % 33])  # Crudely limit to 32 bytes

  def set_tx_pipeline(self, addr=None):
    if addr is not None:
      self.w_register(0x10, self.to_bytes(addr & 0xFFFFFFFFFF, 5)) # Limit to 5 bytes
      # The RX0 pipe must have the same address as TX for ACKs to work
      self.set_rx_pipeline(chan=0, enable=1, addr=addr)

  def destroy(self):
    self.deactivate()
    self.spi.close()

  def from_bytes(self, bytelist):
    # LSByte first!
    ret = 0
    for i in range(0, len(bytelist)):
      ret += bytelist[i]<<i*8
    return ret

  def to_bytes(self, src, listlen=None):
    ret = []
    if listlen is None:
      # Chop & send a byte at a time until src is empty
      while src > 0:
        ret.append(int(src & 255)) # LSByte first!
        src >>= 8
    else:
      # Create a list of the requested length
      for i in range(0, listlen):
        ret.append(int(src & 255)) # LSByte first!
        src >>= 8
    return ret

  def debug_show_pipeconfig(self):
    en_status = self.r_register(0x02, 1)[0]
    for p in range(0, 6):
      en = "ON" if (en_status>>p) & 1 else "off"
      addr = self.from_bytes(self.r_register(0x0A + p, 5))
      bytelen = self.r_register(0x11 + p, 1)[0]
      print("Pipe {:d}: [ {:3s} ] addr: 0x{:010X} -> Payload: {:d} bytes".format(p, en, addr, bytelen))
  
    addr = self.from_bytes(self.r_register(0x10, 5))
    print("Pipe TX:        addr: 0x{:010X}".format(addr))

  def debug_show_config(self):
    stat = self.r_register(0x00, 1)[0]
    print("CONFIG:")
    print ("  " + ("-" * 21))
    registers = ["PRIM_RX","PWR_UP","CRCO","EN_CRC","MASK_MAX_RT","MASK_TX_DS","MASK_RX_DR"]
    for b in reversed(range(0,6)):
      print("  | {:>11s} | {:<3b} |".format(registers[b], stat>>b & 1))
    print ("  " + ("-" * 21))

  def debug_show_status(self):
    stat = self.r_register(0x07, 1)[0]
    print("STATUS:")
    print ("  " + ("-" * 21))
    print ("  | {:>11s} | {:<3b} |".format("RX_DR", stat>>6 & 1))
    print ("  | {:>11s} | {:<3b} |".format("TX_DS", stat>>5 & 1))
    print ("  | {:>11s} | {:<3b} |".format("MAX_RT", stat>>4 & 1))
    print ("  | {:>11s} | {:<03b} |".format("RX_P_NO", stat>>1 & 0b111))
    print ("  | {:>11s} | {:<3b} |".format("TX_FULL", stat & 1))
    print ("  " + ("-" * 21))

  def debug_show_fifo(self):
    stat = self.r_register(0x17, 1)[0]
    print("FIFO:")
    print ("  " + ("-" * 21))
    registers = ["RX_EMPTY","RX_FULL",None,None,"TX_EMPTY","TX_FULL","TX_REUSE"]
    for b in [6, 5, 4, 1, 0]:
      print("  | {:>11s} | {:<3b} |".format(registers[b], stat>>b & 1))
    print ("  " + ("-" * 21))
    print ("  | {:>11s} | {:<3d} |".format("R_RX_PL_WID", self.transfer([0b01100000, 0])[1]))
    print ("  " + ("-" * 21))

  def debug_all(self):
    self.debug_show_status()
    self.debug_show_config()
    self.debug_show_pipeconfig()
    self.debug_show_fifo()
  
##########

