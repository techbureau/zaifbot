"""
this module is for next version
"""

# from zaifbot.exchange.currency_pairs import CurrencyPair
#
#
# class BackTest:
#     def __init__(
#             self, context, currency_pair,
#             entry_rule, exit_rule,
#             stop_rule=None):
#
#         self._context = context
#         self._currency_pair = CurrencyPair(currency_pair)
#         self._entry_rule = entry_rule
#         self._exit_rule = exit_rule
#         self._have_position = False
#         self._stop_rule = stop_rule
#
#     def start(self):
#         self._beginning_task()
#         while self._context.is_continue:
#             self._regular_task()
#             if self._need_stop():
#                 break
#
#             if self._have_position:
#                 self._check_exit()
#             else:
#                 self._check_entry()
#
#     def _entry(self):
#         self._entry_rule.entry(self._context.current_time(),
#                                self._context.current_price())
#
#         self._have_position = True
#
#     def _exit(self):
#         self._exit_rule.exit(self._context.current_time(),
#                              self._context.current_price())
#
#         self._have_position = False
#
#     def _check_entry(self):
#         if self._entry_rule.can_entry():
#             self._entry()
#
#     def _check_exit(self):
#         if self._exit_rule.can_exit():
#             self._exit()
#
#     def _regular_task(self):
#         self._context.update()
#
#     def _beginning_task(self):
#         self._entry_rule.context = self._context
#         self._exit_rule.context = self._context
#         self._context.setup_data(self._currency_pair)
#
#     def _need_stop(self):
#         pass
