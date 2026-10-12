import django_cradmin.uicontainer.semantic
import htmls
from django import test
from django_cradmin import uicontainer


class MinimalContainer(uicontainer.container.AbstractContainerRenderable):
    pass


class TestAbstractContainerRenderable(test.TestCase):
    def test_children_as_kwarg(self):
        container = MinimalContainer(children=[MinimalContainer(), MinimalContainer()])
        self.assertEqual(container.get_childcount(), 2)

    def test_children_with_add_child(self):
        container = MinimalContainer().add_child(MinimalContainer()).add_child(MinimalContainer())
        self.assertEqual(container.get_childcount(), 2)

    def test_children_with_add_children(self):
        container = MinimalContainer().add_children(MinimalContainer(), MinimalContainer())
        self.assertEqual(container.get_childcount(), 2)

    def test_dom_id_default(self):
        container = MinimalContainer()
        self.assertEqual(container.dom_id, False)

    def test_dom_id_default_overridden(self):
        class MyContainer(MinimalContainer):
            def get_default_dom_id(self):
                return "a"

        container = MyContainer()
        self.assertEqual(container.dom_id, "a")

    def test_dom_id_kwarg(self):
        container = MinimalContainer(dom_id="id_a")
        self.assertEqual(container.dom_id, "id_a")

    def test_dom_id_kwarg_invalid(self):
        with self.assertRaises(uicontainer.container.InvalidDomIdError):
            MinimalContainer(dom_id="test")

    def test_dom_id_kwarg_invalid_validation_disabled(self):
        with self.settings(DJANGO_CRADMIN_UICONTAINER_VALIDATE_DOM_ID=False):
            MinimalContainer(dom_id="test")  # No InvalidDomIdError

    def test_role_default(self):
        container = MinimalContainer()
        self.assertEqual(container.role, False)

    def test_role_default_overridden(self):
        class MyContainer(MinimalContainer):
            def get_default_role(self):
                return "a"

        container = MyContainer()
        self.assertEqual(container.role, "a")

    def test_role_kwarg(self):
        container = MinimalContainer(role="a")
        self.assertEqual(container.role, "a")

    def test_get_css_classes_list_default(self):
        container = MinimalContainer(role="a")
        self.assertEqual(container.get_css_classes_list(), [])

    def test_get_css_classes_list_override_default(self):
        class MyContainer(MinimalContainer):
            def get_default_css_classes_list(self):
                return ["a", "b"]

        container = MyContainer()
        self.assertEqual(container.get_css_classes_list(), ["a", "b"])

    def test_get_css_classes_list_css_classes_list_kwarg(self):
        class MyContainer(MinimalContainer):
            def get_default_css_classes_list(self):
                return ["a", "b"]

        container = MyContainer(css_classes_list=["c", "d"])
        self.assertEqual(container.get_css_classes_list(), ["c", "d"])

    def test_get_css_classes_list_extra_css_classes_list_kwarg(self):
        class MyContainer(MinimalContainer):
            def get_default_css_classes_list(self):
                return ["a", "b"]

        container = MyContainer(extra_css_classes_list=["c", "d"])
        self.assertEqual(container.get_css_classes_list(), ["a", "b", "c", "d"])

    def test_get_css_classes_list_css_classes_list_and_extra_css_classes_list_kwarg(self):
        class MyContainer(MinimalContainer):
            def get_default_css_classes_list(self):
                return ["a", "b"]

        container = MyContainer(css_classes_list=["x"], extra_css_classes_list=["c", "d"])
        self.assertEqual(container.get_css_classes_list(), ["x", "c", "d"])

    def test_get_bem_block_kwarg_invalid(self):
        with self.assertRaises(uicontainer.container.InvalidBemError):
            MinimalContainer(bem_block="menu__item")

    def test_get_bem_block_kwarg_invalid_validation_disabled(self):
        with self.settings(DJANGO_CRADMIN_UICONTAINER_VALIDATE_BEM=False):
            MinimalContainer(bem_block="menu__item")  # No InvalidBemError

    def test_get_css_classes_list_bem_block_kwarg(self):
        container = MinimalContainer(bem_block="menu")
        self.assertEqual(container.get_css_classes_list(), ["menu"])

    def test_get_bem_element_kwarg_invalid(self):
        with self.assertRaises(uicontainer.container.InvalidBemError):
            MinimalContainer(bem_element="menu")

    def test_get_bem_element_kwarg_invalid_validation_disabled(self):
        with self.settings(DJANGO_CRADMIN_UICONTAINER_VALIDATE_BEM=False):
            MinimalContainer(bem_element="menu")  # No InvalidBemError

    def test_get_css_classes_list_bem_element_kwarg(self):
        container = MinimalContainer(bem_element="menu__item")
        self.assertEqual(container.get_css_classes_list(), ["menu__item"])

    def test_get_css_classes_list_bem_variants_kwarg(self):
        container = MinimalContainer(bem_element="menu__item", bem_variant_list=["active"])
        self.assertEqual(container.get_css_classes_list(), ["menu__item", "menu__item--active"])

    def test_get_css_classes_list_bem_multiple_variants(self):
        container = MinimalContainer(bem_element="menu__item", bem_variant_list=["active", "large"])
        self.assertEqual(container.get_css_classes_list(), ["menu__item", "menu__item--active", "menu__item--large"])

    def test_get_css_classes_list_get_default_bem_block_or_element(self):
        class MyContainer(MinimalContainer):
            def get_default_bem_block_or_element(self):
                return "menu"

        container = MyContainer()
        self.assertEqual(container.get_css_classes_list(), ["menu"])

    def test_get_css_classes_list_get_default_bem_variant_list(self):
        class MyContainer(MinimalContainer):
            def get_default_bem_variant_list(self):
                return ["expanded"]

        container = MyContainer(bem_block="menu")
        self.assertEqual(container.get_css_classes_list(), ["menu", "menu--expanded"])

    def test_get_css_classes_list_bem_does_not_affect_other_css_classes(self):
        container = MinimalContainer(bem_block="menu", bem_variant_list=["expanded"], css_classes_list=["someclass"])
        self.assertEqual(container.get_css_classes_list(), ["menu", "menu--expanded", "someclass"])

    def test_iter_children(self):
        container = MinimalContainer(children=[MinimalContainer(dom_id="id_a"), MinimalContainer(dom_id="id_b")])
        children = list(container.iter_children())
        self.assertEqual(children[0].dom_id, "id_a")
        self.assertEqual(children[1].dom_id, "id_b")

    def test_get_html_element_attributes_default(self):
        container = MinimalContainer()
        with self.settings(DJANGO_CRADMIN_INCLUDE_TEST_CSS_CLASSES=False):
            self.assertEqual(
                container.get_html_element_attributes(),
                {
                    "role": False,
                    "id": False,
                    "class": False,
                },
            )

    def test_get_html_element_attributes_role(self):
        container = MinimalContainer(role="a")
        self.assertEqual(container.get_html_element_attributes()["role"], "a")

    def test_get_html_element_attributes_dom_id(self):
        container = MinimalContainer(dom_id="id_a")
        self.assertEqual(container.get_html_element_attributes()["id"], "id_a")

    def test_get_html_element_attributes_dom_css_classes(self):
        container = MinimalContainer(css_classes_list=["a", "b"])
        self.assertEqual(
            set(container.get_html_element_attributes()["class"].split()),
            {"a", "b", "test-uicontainer-minimalcontainer"},
        )

    def test_html_element_attributes_string_default(self):
        container = MinimalContainer()
        with self.settings(DJANGO_CRADMIN_INCLUDE_TEST_CSS_CLASSES=False):
            self.assertEqual(container.html_element_attributes_string, "")

    def test_html_element_attributes_string_role(self):
        container = MinimalContainer(role="a")
        with self.settings(DJANGO_CRADMIN_INCLUDE_TEST_CSS_CLASSES=False):
            self.assertEqual(container.html_element_attributes_string, ' role="a"')

    def test_html_element_attributes_string_dom_id(self):
        container = MinimalContainer(dom_id="id_a")
        with self.settings(DJANGO_CRADMIN_INCLUDE_TEST_CSS_CLASSES=False):
            self.assertEqual(container.html_element_attributes_string, ' id="id_a"')

    def test_html_element_attributes_string_css_classes(self):
        container = MinimalContainer(css_classes_list=["a"])
        with self.settings(DJANGO_CRADMIN_INCLUDE_TEST_CSS_CLASSES=False):
            self.assertEqual(container.html_element_attributes_string, ' class="a"')

    def test_html_element_attributes_string_html_element_attributes_kwarg(self):
        container = MinimalContainer(html_element_attributes={"a": "10"})
        with self.settings(DJANGO_CRADMIN_INCLUDE_TEST_CSS_CLASSES=False):
            self.assertEqual(container.html_element_attributes_string, ' a="10"')

    def test_prepopulate_children_list_default(self):
        container = MinimalContainer()
        self.assertEqual(container.get_childcount(), 0)

    def test_prepopulate_children_list_overridden_no_other_children_added(self):
        the_child = MinimalContainer()

        class MyContainer(MinimalContainer):
            def prepopulate_children_list(self):
                return [the_child]

        container = MyContainer()
        self.assertEqual(container.get_childcount(), 1)
        self.assertEqual(list(container.iter_children())[0], the_child)

    def test_prepopulate_children_list_overridden_other_children_added(self):
        class MyContainer(MinimalContainer):
            def prepopulate_children_list(self):
                return [MinimalContainer(dom_id="id_a")]

        container = MyContainer(children=[MinimalContainer(dom_id="id_b")])
        children = list(container.iter_children())
        self.assertEqual(children[0].dom_id, "id_a")
        self.assertEqual(children[1].dom_id, "id_b")

    def test_prepopulate_virtual_children_list_default(self):
        container = MinimalContainer()
        self.assertEqual(container.get_virtual_childcount(), 0)

    def test_prepopulate_virtual_children_list_overridden_no_other_children_added(self):
        the_child = MinimalContainer()

        class MyContainer(MinimalContainer):
            def prepopulate_virtual_children_list(self):
                return [the_child]

        container = MyContainer()
        self.assertEqual(container.get_virtual_childcount(), 1)
        self.assertEqual(list(container.iter_virtual_children())[0], the_child)

    def test_wrapper_element_can_have_children(self):
        container = MinimalContainer()
        self.assertTrue(container.can_have_children)

    def test_wrapper_element_can_have_children_false_can_not_add_children(self):
        class MyContainer(MinimalContainer):
            @property
            def can_have_children(self):
                return False

        container = MyContainer()
        with self.assertRaises(uicontainer.container.NotAllowedToAddChildrenError):
            container.add_child(MinimalContainer())

    def test_wrapper_element_can_have_children_uses_html_tag_supports_children(self):
        self.assertTrue(MinimalContainer().can_have_children)

        class OverriddenContainer(MinimalContainer):
            @property
            def html_tag_supports_children(self):
                return False

        self.assertFalse(OverriddenContainer().can_have_children)

    def test_bootstrap(self):
        container = MinimalContainer()
        self.assertFalse(hasattr(container, "parent"))
        self.assertFalse(container._is_bootstrapped)
        container.bootstrap()
        self.assertTrue(hasattr(container, "parent"))
        self.assertTrue(container._is_bootstrapped)

    def test_bootstrap_with_parent(self):
        container = MinimalContainer()
        child = MinimalContainer()
        container.add_child(child)
        container.bootstrap()
        self.assertEqual(child.parent, container)

    def test_bootstrap_already_bootstrapped(self):
        container = MinimalContainer()
        container.bootstrap()
        with self.assertRaises(uicontainer.container.AlreadyBootsrappedError):
            container.bootstrap()

    def test_bootstrap_already_bootstrapped_deep(self):
        container = MinimalContainer()
        child = MinimalContainer()
        container.add_child(child)
        child.bootstrap()
        with self.assertRaises(uicontainer.container.AlreadyBootsrappedError):
            container.bootstrap()

    def test_render_sanity(self):
        container = MinimalContainer().bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.count("div"), 1)

    def test_render_dom_id(self):
        container = MinimalContainer(dom_id="id_mycontainer").bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("div")["id"], "id_mycontainer")

    def test_render_role(self):
        container = MinimalContainer(role="main").bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("div")["role"], "main")

    def test_render_cssclass(self):
        container = MinimalContainer(css_classes_list=["a"]).bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("div").cssclasses_set, {"a", "test-uicontainer-minimalcontainer"})

    def test_render_html_element_attributes(self):
        container = MinimalContainer(html_element_attributes={"my-attribute": "test"}).bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("div")["my-attribute"], "test")

    def test_render_with_children(self):
        container = MinimalContainer(
            dom_id="id_main",
            children=[
                MinimalContainer(dom_id="id_child1"),
                MinimalContainer(dom_id="id_child2"),
            ],
        ).bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.count("div"), 3)
        self.assertTrue(selector.exists("div#id_main"))
        self.assertTrue(selector.exists("div#id_main > div#id_child1"))
        self.assertTrue(selector.exists("div#id_main > div#id_child2"))

    def test_render_with_children_deep(self):
        container = MinimalContainer(
            dom_id="id_main",
            children=[
                MinimalContainer(
                    dom_id="id_child1",
                    children=[
                        MinimalContainer(dom_id="id_child1_1"),
                    ],
                ),
                MinimalContainer(dom_id="id_child2"),
            ],
        ).bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.count("div"), 4)
        self.assertTrue(selector.exists("div#id_main"))
        self.assertTrue(selector.exists("div#id_main > div#id_child1"))
        self.assertTrue(selector.exists("div#id_main > div#id_child1 > div#id_child1_1"))
        self.assertTrue(selector.exists("div#id_main > div#id_child2"))

    def test_should_render_false(self):
        class MyContainer(MinimalContainer):
            @property
            def should_render(self):
                return False

        container = MyContainer().bootstrap()
        self.assertEqual(container.render(), "")


class TestDivRenderable(test.TestCase):
    def test_sanity(self):
        container = uicontainer.container.Div().bootstrap()
        selector = htmls.S(container.render())
        self.assertTrue(selector.exists("div"))


class TestSectionRenderable(test.TestCase):
    def test_sanity(self):
        container = django_cradmin.uicontainer.semantic.Section().bootstrap()
        selector = htmls.S(container.render())
        self.assertTrue(selector.exists("section"))


class TestHeaderRenderable(test.TestCase):
    def test_sanity(self):
        container = django_cradmin.uicontainer.semantic.Header().bootstrap()
        selector = htmls.S(container.render())
        self.assertTrue(selector.exists("header"))


class TestMainRenderable(test.TestCase):
    def test_sanity(self):
        container = django_cradmin.uicontainer.semantic.Main().bootstrap()
        selector = htmls.S(container.render())
        self.assertTrue(selector.exists("main"))

    def test_default_role_is_main(self):
        container = django_cradmin.uicontainer.semantic.Main().bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("main")["role"], "main")
