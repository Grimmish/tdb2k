import bens_rf24
import time
from pixelcharmap import mono3x5,pixart
from menumap import mainmenu

class rf24_headunit():
  def __init__(self, radio, addr=0xE7E7E7E7E7):
    self.radio = radio
    self.addr = addr
    self.display = BicolorMatrix16x8()
    self.menu = MenuSystem(mainmenu)

  # Break the 16-bit framebuffer rows into 8-bit words
  def fbreducer(self, c, i):
    c.extend([i>>8, i & 0xFF])
    return c

  def sendBuffer(self):
    self.radio.set_tx_pipeline(self.addr)
    gamma = [ord('D'), ord('b'), self.display.fb['b']]
    rchan = [ord('D'), ord('R')] + reduce(self.fbreducer, self.display.fb['R'], [])
    gchan = [ord('D'), ord('G')] + reduce(self.fbreducer, self.display.fb['G'], [])
    self.radio.w_tx_payload(gamma)
    self.radio.w_tx_payload(rchan)
    self.radio.w_tx_payload(gchan)
    # Switch radio channel-0 back to its original "listener" address
    self.radio.set_rx_pipeline(chan=0, addr=self.radio.addr)
    return True

  # NOTE! This hideous thing blocks until it's finished!
  # New matrix will slide out in 'direction', chased by new matrix. Thus
  # scrolling south through a list will slide in the (U)p direction.
  # The right-most 3 columns containing navigation widgets (up/down/select)
  # are locked/ignored and do not change.
  def slideTransition(self, direction, newmatrix, timestep):
    if direction.upper()[0] == 'L':
      for i in range(13):
        if (i > 0): time.sleep(timestep)
        for y in range(8):
          for c in ['R', 'G']:
            # Shift unmasked portion by one pixel & re-merge with static section
            self.display.fb[c][y] = ((self.display.fb[c][y] & 0xFFF8)<<1) \
                                    | (self.display.fb[c][y] & 7) & 0xFFFF
            self.display.fb[c][y] |= (newmatrix.fb[c][y]>>(12-i)) & 0xFFF8
        self.sendBuffer()
      return True
    elif direction.upper()[0] == 'R':
      for i in range(13):
        if (i > 0): time.sleep(timestep)
        for y in range(8):
          for c in ['R', 'G']:
            self.display.fb[c][y] = ((self.display.fb[c][y]>>1) & 0xFFF8) \
                                    | (self.display.fb[c][y] & 7) & 0xFFFF
            self.display.fb[c][y] |= ((newmatrix.fb[c][y] & 0xFFF8)<<(12-i)) & 0xFFF8
        self.sendBuffer()
      return True
    elif direction.upper()[0] == 'U':
      for i in range(8):
        if (i > 0): time.sleep(timestep)
        for y in range(7):
          for c in ['R', 'G']:
            self.display.fb[c][y] = (self.display.fb[c][y+1] & 0xFFF8) \
                                    | (self.display.fb[c][y] & 7)
        for c in ['R', 'G']:
          self.display.fb[c][7] = (newmatrix.fb[c][i] & 0xFFF8) \
                                  | (self.display.fb[c][7] & 7)
        self.sendBuffer()
      return True
    elif direction.upper()[0] == 'D':
      for i in range(8):
        if (i > 0): time.sleep(timestep)
        for y in range(7,0,-1):
          for c in ['R', 'G']:
            self.display.fb[c][y] = (self.display.fb[c][y-1] & 0xFFF8) \
                                    | (self.display.fb[c][y] & 7)
        for c in ['R', 'G']:
          self.display.fb[c][0] = (newmatrix.fb[c][7-i] & 0xFFF8) \
                                  | (self.display.fb[c][0] & 7)
        self.sendBuffer()
      return True
    else: return False
  
  def buildMenuMatrix(self, menuitem):
    matrix = BicolorMatrix16x8()
    matrix.floodColor('B')
    matrix.drawPixart('pointerup', 13, 0, 'R')
    matrix.drawPixart('2x2square', 14, 3, 'Y')
    matrix.drawPixart('pointerdown', 13, 6, 'G')
    if menuitem['labeltype'] == 'string':
      matrix.drawString(menuitem['label'], 0, 1, 'Y')
    elif menuitem['labeltype'] == 'pixart':
      matrix.drawPixart(menuitem['label'], 0, 0, 'Y')
    else:
      matrix.drawString('??', 1, 1, 'R')
    # UI hints based on type
    if 'submenu' in menuitem:
      matrix.drawPixel(12, 3, 'Y')
      matrix.drawPixel(12, 4, 'Y')
    return matrix

  def drawCurrentMenuItem(self):
    sm = self.menu
    self.display = self.buildMenuMatrix(sm.currentlist[sm.currentitem])
    self.sendBuffer()

  # 'action' should be one of ['up', 'down', 'select']
  def menuAction(self, action):
    if action[0].upper() == 'S':
      slidedirection = None
      thisitem = self.menu.currentlist[self.menu.currentitem]
      if 'dofunction' in thisitem:
        thisitem = thisitem['dofunction'](thisitem, thisitem['do_args'])
        self.menu.replaceItem(self.menu.currentlevel, self.menu.currentitem, thisitem)
      if 'submenu' in thisitem:
        self.menu.currentlevel += [ self.menu.currentitem ]
        self.menu.currentitem = 0
        slidedirection = 'left'
      if 'backbutton' in thisitem:
        self.menu.currentitem = self.menu.currentlevel.pop()
        slidedirection = 'right'

    elif action[0].upper() == 'U':
      self.menu.currentitem -= 1
      slidedirection = 'down'
    elif action[0].upper() == 'D':
      self.menu.currentitem += 1
      slidedirection = 'up'
    else:
      return False
     
    self.menu.currentlist = self.menu.getChoices(self.menu.currentlevel)
    if self.menu.currentitem < 0:
      self.menu.currentitem += len(self.menu.currentlist)
    elif self.menu.currentitem >= len(self.menu.currentlist):
      self.menu.currentitem -= len(self.menu.currentlist)

    # FIXME Future "showfunction" feature probaby happens here
    drawitem = self.menu.currentlist[self.menu.currentitem]
    if 'showfunction' in drawitem:
      drawitem = drawitem['showfunction'](drawitem, drawitem['show_args'])
    newmatrix = self.buildMenuMatrix(drawitem)
    if slidedirection:
      return self.slideTransition(slidedirection, newmatrix, 0.03)
    else:
      return self.drawCurrentMenuItem()

class BicolorMatrix16x8():
  def __init__(self):
    # Framebuffer is eight rows, each row representing
    # 16 bits of width. Two color channels.
    self.fb = { 'b': 15, # Brightness: 0 - 15
                'R': [0,0,0,0,0,0,0,0],
                'G': [0,0,0,0,0,0,0,0] }

  # 0,0 is top-left
  def drawPixel(self, x, y, color):
    if not ((-1 < x < 16) and (-1 < y < 8)):
      return False
    if color[0].upper() == 'R' or color[0].upper() == 'Y':
      self.fb['R'][y] |= 1<<(15 - x)
    else:
      self.fb['R'][y] &= ~(1<<(15-x))
    if color[0].upper() == 'G' or color[0].upper() == 'Y':
      self.fb['G'][y] |= 1<<(15 - x)
    else:
      self.fb['G'][y] &= ~(1<<(15-x))
    return True

  def setBrightness(self, bright):
    if (0 < bright < 16):
      self.fb['b'] = bright
      return True
    else:
      return False

  # Upper-left corner of character will be rooted at x/y
  def drawChar(self, char, x, y, color):
    charmapwidth = 3
    if not char in mono3x5:
      return False
    for cy in range(len(mono3x5[char])):
      for cx in range(charmapwidth):
        if (mono3x5[char][cy] & 1<<cx):
          self.drawPixel(x+(charmapwidth-1-cx), y+cy, color)
    return True

  # Upper-left corner will be rooted at x/y
  def drawPixart(self, img, x, y, color):
    if not img in pixart:
      return False
    for cy in range(8):
      for cx in range(16):
        if (pixart[img][cy] & 1<<cx):
          self.drawPixel(x+(16-1-cx), y+cy, color)
    return True

  def drawString(self, st, x, y, color):
    for z in range(len(st)):
      self.drawChar(st[z], x+(4*z), y, color)

  def floodColor(self, color):
    if color[0].upper() == 'R' or color[0].upper() == 'Y':
      self.fb['R'] = [0xFFFF,0xFFFF,0xFFFF,0xFFFF,0xFFFF,0xFFFF,0xFFFF,0xFFFF]
    else:
      self.fb['R'] = [0,0,0,0,0,0,0,0]
    if color[0].upper() == 'G' or color[0].upper() == 'Y':
      self.fb['G'] = [0xFFFF,0xFFFF,0xFFFF,0xFFFF,0xFFFF,0xFFFF,0xFFFF,0xFFFF]
    else:
      self.fb['G'] = [0,0,0,0,0,0,0,0]


class MenuSystem():
  def __init__(self, menutree, startlevel=[], startitem=0):
    self.tree = menutree;
    # currentlevel is a list representing the index-based path to
    # reach a given submenu (i.e., the navigation sequence to reach "here")
    #   Examples:
    #     []    : Root menu
    #     [0,2] : First submenu, then third submenu
    self.currentlevel = startlevel if self.isValidLevel(startlevel) else []
    self.currentlist = self.getChoices(self.currentlevel)
    self.currentitem = startitem if self.isValidItem(startlevel, startitem) else 0

  def isValidLevel(self, menulevel):
    if menulevel == []: return True
    choices = self.tree;
    for z in range(len(menulevel)):
      try:
        choices = choices[menulevel[z]]["submenu"]
      except:
        return False
    return True

  def isValidItem(self, menulevel, menuitem):
    validchoices = self.getChoices(menulevel)
    if menuitem >= 0 and menuitem < len(validchoices):
      return True
    else:
      return False

  def getChoices(self, menulevel):
    if not self.isValidLevel(menulevel): return []
    choices = self.tree;
    for z in range(len(menulevel)):
      choices = choices[menulevel[z]]["submenu"]
    return choices

  def replaceItem(self, menulevel, menuitem, newobject):
    if not self.isValidItem(menulevel, menuitem):
      return False
    layer = self.tree;
    for z in range(len(menulevel)):
      try:
        layer = layer[menulevel[z]]["submenu"]
      except:
        return False
    layer[menuitem] = newobject
    return True
    
##########
