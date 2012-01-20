Ext.define('devilry.extjshelpers.ComboboxTemplatesMixin', {
    assignmentRowTpl: [
        '<div class="section popuplistitem">',
        '   <p class="path">{parentnode__parentnode__short_name}.{parentnode__short_name}</p>',
        '   <h1>{long_name:ellipsis(40)}</h1>',
        '</div>'
    ],

    assignmentgroupRowTpl: [
        '<div class="section popuplistitem">',
        '   <p class="path">',
        '{parentnode__parentnode__parentnode__short_name:ellipsis(60)}.',
        '{parentnode__parentnode__short_name:ellipsis(60)}.',
        '{parentnode__short_name:ellipsis(60)}',
        '   </p>',
        '   <tpl if="!is_student">',
        '       <h1><ul class="useridlist"><tpl for="candidates__identifier"><li>{.}</li></tpl></ul></h1>',
        '   </tpl>',
        '   <tpl if="is_student">',
        '       <h1>{parentnode__long_name:ellipsis(40)}</h1>',
        '   </tpl>',
        '   <p><tpl if="name">{name}</tpl><p>',
        '</div>'
    ],

    deliveryRowTpl: [
        '<div class="section popuplistitem">',
        '   <p class="path">',
        '{deadline__assignment_group__parentnode__parentnode__parentnode__short_name}.',
        '{deadline__assignment_group__parentnode__parentnode__short_name}.',
        '{deadline__assignment_group__parentnode__short_name}',
        '   </p>',
        '   <tpl if="!is_student">',
        '       <ul class="useridlist"><tpl for="deadline__assignment_group__candidates__identifier"><li>{.}</li></tpl></ul>',
        '   </tpl>',
        '   <tpl if="deadline__assignment_group__name"> &ndash; {deadline__assignment_group__name}</tpl>',
        '   <div class="section dl_valueimportant">',
        '      <div class="section">',
        '          <h1>Delivery number</h1>',
        '          {number}',
        '      </div>',
        '   </div>',
        '</div>'
    ]
});
