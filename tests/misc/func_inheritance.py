#!/usr/bin/env python

class A(object):
    def __init__(self):
        super(A, self).__init__()
        return

    def say_something(self):
        print 'I\'m class A'
        return

    def call_me(self):
        self.say_something()
        return


class B(A):
    def __init__(self):
        super(B, self).__init__()
        return

    def say_something(self):
        print 'I\'m class B'
        return

    def call_me(self):
        super(B, self).call_me()
        return


if __name__ == '__main__':
    """
    Test if class B prints out "I'm class B" when call_me() is called. This
    determines if called functions from inherited classes call the overwritten
    or original function.

    Results:
        "I'm class B" is printed. This shows that overwritten functions are
        used.
    """
    b = B()
    b.call_me()
