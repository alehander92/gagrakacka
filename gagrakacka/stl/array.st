Array extend [
  collect: aBlock [
    | results |
    results := Array new.
    results printNl.
    'lalalalalalalalalala' printNl.
    self each: [:element |
      results push: (aBlock value: element)
    ].
    ^ results
  ]

  select: aBlock [
    | results |
    results := Array new.
    self each: [:element |
      (aBlock value: element) ifTrue: [
        results push: element
      ]
    ].
    ^ results
  ]
]
