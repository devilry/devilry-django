// ----------------------------------------------------------------------------
// markItUp!
// ----------------------------------------------------------------------------
// Copyright (C) 2008 Jay Salvat
// http://markitup.jaysalvat.com/
// ----------------------------------------------------------------------------
// Html tags
// http://en.wikipedia.org/wiki/html
// ----------------------------------------------------------------------------
// Basic set. Feel free to add more tags
// ----------------------------------------------------------------------------
markitupRstSettings = {
	//onShiftEnter:  	{keepDefault:false, replaceWith:'<br />\n'},
	//onCtrlEnter:  	{keepDefault:false, openWith:'\n<p>', closeWith:'</p>'},
	//onTab:    		{keepDefault:false, replaceWith:'    '},
	//markupSet:  [ 	
		//{name:'Bold', key:'B', openWith:'(!(<strong>|!|<b>)!)', closeWith:'(!(</strong>|!|</b>)!)' },
		//{name:'Italic', key:'I', openWith:'(!(<em>|!|<i>)!)', closeWith:'(!(</em>|!|</i>)!)'  },
		//{name:'Stroke through', key:'S', openWith:'<del>', closeWith:'</del>' },
		//{separator:'---------------' },
		//{name:'Picture', key:'P', replaceWith:'<img src="[![Source:!:http://]!]" alt="[![Alternative text]!]" />' },
		//{name:'Link', key:'L', openWith:'<a href="[![Link:!:http://]!]"(!( title="[![Title]!]")!)>', closeWith:'</a>', placeHolder:'Your text to link...' },
		//{separator:'---------------' },
		//{name:'Clean', className:'clean', replaceWith:function(markitup) { return markitup.selection.replace(/<(.*?)>/g, "") } },		
		//{name:'Preview', className:'preview',  call:'preview'}
	//]

	previewParserPath: DEVILRY_MAIN_PAGE + '/ui/rst_to_html',
	previewParserVar: 'rst',
	//previewAutoRefresh: true,
	resizeHandle: true,
	onShiftEnter: {keepDefault:false, openWith:'\n\n'},
	onTab: {keepDefault:false, replaceWith:'    '},
	markupSet: [
		{name:'Heading 1', key:'1', placeHolder:'Your title here...', closeWith:function(markItUp) { return miu.markdownTitle(markItUp, '#') } },
		{name:'Heading 2', key:'2', placeHolder:'Your title here...', closeWith:function(markItUp) { return miu.markdownTitle(markItUp, '=') } },
		{name:'Heading 3', key:'3', placeHolder:'Your title here...', closeWith:function(markItUp) { return miu.markdownTitle(markItUp, '-') } },
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


// mIu nameSpace to avoid conflict.
miu = {
	markdownTitle: function(markItUp, char) {
		heading = '';
		linewidth = 70;
		for(i = 0; i < linewidth; i++) {
			heading += char;
		}
		return '\n'+heading;
	}
}
