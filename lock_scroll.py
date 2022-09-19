import sublime
import sublime_plugin
from sublime import Region, DRAW_NO_OUTLINE, DRAW_EMPTY

sync_running = False

def set_ruler_offset_from_visible(view, additional_offset):
	"""
	additional_offset:
		Additional offset from the visible region. Needed since viewport
		position doesn't update immdediately 
	"""
	visible_region = view.visible_region()
	ruler_pos = 80
	offset = visible_region.begin() - view.lines(visible_region)[0].begin()
	view.settings().set('rulers', [ruler_pos + offset + additional_offset])

class ScrollListener(sublime_plugin.EventListener):
	old_pos = None

	def on_text_command(self, view, command_name, args):
		if sync_running:
			self.old_pos = view.viewport_position()

	def on_post_text_command(self, view, command_name, args):
		if sync_running:
			new_pos = view.viewport_position()
			if self.old_pos is None:
				self.old_pos = new_pos
			if command_name != 'scroll_width':
				# NOTE: when locked, we get the new y pos, but not the new xpos
				view.set_viewport_position((self.old_pos[0], new_pos[1]), False)
				additional_offset = 0
			else:
				# NOTE: check if we are moving left or right
				tab_size = view.settings().get('tab_size', 4)
				if new_pos[0] > self.old_pos[0]:
					additional_offset = tab_size
				else:
					additional_offset = -1 * tab_size

			# NOTE: when locked, update the ruler with scroll width commands
			set_ruler_offset_from_visible(view, additional_offset)

class LockScrollCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global sync_running
		current_state = self.view.settings().get('lock_scroll')
		self.view.settings().set('lock_scroll', not current_state)
		sync_running = current_state

		if sync_running:
			set_ruler_offset_from_visible(self.view, 0)
		else:
			self.view.settings().set('rulers', [])
