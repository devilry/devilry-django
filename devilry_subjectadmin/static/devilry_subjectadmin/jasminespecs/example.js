describe("Basic Assumptions", function() {
    it("has ExtJS4 loaded", function() {
        expect(Ext).toBeDefined();
        expect(Ext.getVersion()).toBeTruthy();
        expect(Ext.getVersion().major).toEqual(4);
    });

    it("has loaded subjectadmin code",function(){
        expect(subjectadmin).toBeDefined();
    });
});
