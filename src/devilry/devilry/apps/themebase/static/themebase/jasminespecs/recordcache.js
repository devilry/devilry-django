Ext.syncRequire('themebase.RecordCache');

describe("RecordCache", function() {
    //console.log(application);
    var FakeModel, fakeStore, recordCache;

    beforeEach(function() {
        FakeModel = Ext.define('FakeModel', {
            extend: 'Ext.data.Model',
            fields: ['id', 'title'],
            proxy: 'memory'
        });
        fakeStore = Ext.create('Ext.data.Store', {
            model: FakeModel,
            data: [{
                id: 0,
                title:'duck1100'
            }, {
                id: 1,
                title:'duck1100'
            }, {
                id: 2,
                title:'duck-mek2030'
            }]
        });
        recordCache = Ext.create('themebase.RecordCache', {
            model: FakeModel,
            stores: [fakeStore]
        });
    }),

    it("_findByInStore Works", function() {
        var duck1100 = recordCache._findByInStores(function(record) {
            return record.get('id') == 1;
        }, this);
        expect(duck1100).toNotEqual(null);
        expect(duck1100.get('title')).toEqual('duck1100');

        var nomatch = recordCache._findByInStores(function(record) {
            return record.get('id') == 20000;
        }, this);
        expect(nomatch).toBeNull();
    });

    it("_findByInCache Works", function() {
        var nomatch = recordCache._findByInCache(function(record) {
            return record.get('id') == 2;
        }, this);
        expect(nomatch).toBeNull();

        recordCache.put(new FakeModel({
            id: 2,
            title: 'Hello world'
        }));
        var helloworld = recordCache._findByInCache(function(record) {
            return record.get('id') == 2;
        }, this);
        expect(helloworld).toNotEqual(null);
        expect(helloworld.get('id')).toEqual(2);
        expect(helloworld.get('title')).toEqual('Hello world');
    });

    it("findBy Works", function() {
        recordCache.put(new FakeModel({
            id: 2,
            title: 'Hello world'
        }));

        var nomatch = recordCache.findBy(function(record) {
            return record.get('id') == 2000;
        }, this);
        expect(nomatch).toBeNull();

        var duck1100 = recordCache.findBy(function(record) {
            return record.get('id') == 1;
        }, this);
        expect(duck1100).toNotEqual(null);
        expect(duck1100.get('title')).toEqual('duck1100');

        var helloworld = recordCache.findBy(function(record) {
            return record.get('id') == 2;
        }, this);
        expect(helloworld).toNotEqual(null);
        expect(helloworld.get('id')).toEqual(2);
        expect(helloworld.get('title')).toEqual('Hello world');
    });
});
