import sublime
import sublime_plugin

sync_running = False

class ScrollListener(sublime_plugin.EventListener):
	def on_text_command(self, view, command_name, args):
		if sync_running and command_name != 'scroll_width':
			self.old_pos = view.viewport_position()

	def on_post_text_command(self, view, command_name, args):
		if sync_running and command_name != 'scroll_width':
			new_pos = view.viewport_position()
			view.set_viewport_position((self.old_pos[0], new_pos[1]), False)
		# if(command_name == 'move'):
			# return (command_name, args)

class LockScrollCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global sync_running
		current_state = self.view.settings().get('lock_scroll')
		self.view.settings().set('lock_scroll', not current_state)
		sync_running = current_state