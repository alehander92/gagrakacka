Boolean := Object subclass: #Boolean.

True  := Boolean subclass: #True.
False := Boolean subclass: #False.

True extend [
  ifTrue: if ifFalse: else [
    ^ if value ]

  ifFalse: else ifTrue: if [
    ^ if value ]

  ifTrue: if [
    ^ if value ]

  ifFalse: else [
    nil ]

  & other [
    other ]

  | other [
    self ]

  asString [
    'true' ]
]

False extend [
  ifTrue: if ifFalse: else [
    ^ else value ]

  ifFalse: else ifTrue: if [
    ^ else value ]

  ifTrue: if [
    ^ nil ]

  ifFalse: else [
    ^ else value ]

  & other [
    ^ other ]

  | other [
    ^ self ]

  asString [
    ^ 'false' ]
].

false := False new.
true  := True  new
