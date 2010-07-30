markitupRstSettings = {
	previewParserPath: DEVILRY_MAIN_PAGE + '/ui/preview_rst',
	previewParserVar: 'rst',
	//previewAutoRefresh: true,
	resizeHandle: true,
	onShiftEnter: {keepDefault:false, openWith:'\n\n'},
	onTab: {keepDefault:false, replaceWith:'    '},
	markupSet: [
		{name:'Heading 1', key:'1', placeHolder:'Your title here...', openWith:'\n', closeWith:'\n######################################################################' },
		{name:'Heading 2', key:'2', placeHolder:'Your title here...', openWith:'\n', closeWith:'\n======================================================================' },
		{name:'Heading 3', key:'3', placeHolder:'Your title here...', openWith:'\n', closeWith:'\n----------------------------------------------------------------------' },
		{separator:'---------------' },		
		{name:'Bold', key:'B', openWith:'**', closeWith:'**'},
		{name:'Italic', key:'I', openWith:'*', closeWith:'*'},
		{separator:'---------------' },
		{name:'Bulleted List', openWith:'- ' },
		{name:'Numeric List', openWith:'#. ' },
		{separator:'---------------' },
		{name:'Link', key:'L', openWith:'`', closeWith:' <[![Url:!:http://]!]>`_', placeHolder:'Link title here...' },
		{separator:'---------------'},	
		{name:'Code Block / Code', openWith:'::\n\n    ', placeHolder:'Code indented with 4 spaces (tab-key inserts 4 spaces)...'},
		{separator:'---------------'},
		{name:'Preview', call:'preview', className:"preview"}
	]
}
