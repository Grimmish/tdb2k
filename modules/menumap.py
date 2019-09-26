#
# Menu trees & subtrees
#
# Described as lists of items; those items may also contain lists
#
# Mandatory properties for every item:
#     label : How to visualize this element
#     labeltype : Nature of the 'label'. One of:
#                   - string
#                   - pixart
#     labelcolor : OPTIONAL - One of 'R', 'G', or 'Y' (defaults to 'Y')
#
# Optional properties that shape behavior:
#     dofunction : If defined, this function will be invoked when the item is
#                  selected. THIS BEHAVIOR ALWAYS HAPPENS FIRST.
#                  Called with two args: current menu item, and 'do_args'.
#                  IMPORTANT: [current menu item] WILL BE SET TO THE RESULT OF
#                             THIS FUNCTION! If you don't wish to modify it,
#                             just return the first argument unchanged.
#     do_args : Mandatory if 'dofunction' is defined. Contains a list object
#               that will be passed to dofunction() as the second argument.
#     showfunction : Works like "dofunction" above, but is executed just before
#                    the item is displayed. Like dofunction, the return value of
#                    becomes the new value for [current menu item].
#     show_args : Mandatory if 'showfunction' is defined. Similar to 'do_args',
#                 is a list object that will be passed to showfunction() as
#                 the second argument.
#     submenu : If defined, will descend into a further sublayer of menus
#               within this object, following the same rules as the top-level
#               menu definition. If a "dofunction" is also defined, it will be
#               processed before navigating into the submenu.
#     backbutton : Boolean value; if defined (and True), selecting this item
#                  will navigate one level backwards (upwards?) in the menu.
#                  Logically this should never be defined simultaenously with
#                  submenu, but hey man, you do you.
# 
#
# NOTE! These trees are subject to change after initialization; 'dofunction'
#       and 'do_args' values will be added later, and may in turn make
#       dramatic changes to the in-memory tree.
#
configmenu = [
  {
    'label': 'DSP',
    'labeltype': 'string',
  },
  {
    'label': 'GHO',
    'labeltype': 'string',
  },
  {
    'label': 'ALP',
    'labeltype': 'string',
    'submenu': [
      {
        'label': "AAA",
        'labeltype': 'string',
      },
      {
        'label': "BBB",
        'labeltype': 'string',
      },
      {
        'label': "CCC",
        'labeltype': 'string',
      },
      {
        'label': 'goback',
        'labeltype': 'pixart',
        'backbutton': True
      }
    ]
  },
  {
    'label': 'YYY',
    'labeltype': 'string',
  },
  {
    'label': 'goback',
    'labeltype': 'pixart',
    'backbutton': True
  }
]

infomenu = [
  {
    'label': 'battery',
    'labeltype': 'pixart',
  },
  {
    'label': 'target',
    'labeltype': 'pixart',
  },
  {
    'label': 'startbeam',
    'labeltype': 'pixart',
  },
  {
    'label': 'stopbeam',
    'labeltype': 'pixart',
  },
  {
    'label': 'goback',
    'labeltype': 'pixart',
    'backbutton': True
  }
]

mainmenu = [
  {
    'label': 'WHO',
    'labeltype': 'string',
    'submenu': [
      {
        'label': 'ADA',
        'labeltype': 'string',
      },
      {
        'label': 'RDO',
        'labeltype': 'string',
      },
      {
        'label': 'goback',
        'labeltype': 'pixart',
        'backbutton': True
      }
    ]
  },
  {
    'label': 'DIF',
    'labeltype': 'string',
    'submenu': [
      {
        'label': 'PTD',
        'labeltype': 'string',
      },
      {
        'label': 'FTD',
        'labeltype': 'string',
      },
      {
        'label': 'PRV',
        'labeltype': 'string',
      },
      {
        'label': 'OFF',
        'labeltype': 'string',
      },
      {
        'label': 'goback',
        'labeltype': 'pixart',
        'backbutton': True
      }
    ]
  },
  {
    'label': 'CFG',
    'labeltype': 'string',
    'submenu': configmenu
  },
  {
    'label': 'INF',
    'labeltype': 'string',
    'submenu': infomenu
  }
]
