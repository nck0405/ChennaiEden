# -*- coding: utf-8 -*-

from gluon import current
from s3 import *
from s3layouts import *
try:
    from .layouts import *
except ImportError:
    pass
import s3menus as default

# =============================================================================
class S3MainMenu(default.S3MainMenu):
    """ Custom Application Main Menu """

    # -------------------------------------------------------------------------
    @classmethod
    def menu(cls):
        """ Compose Menu """

        # Modules menus
        main_menu = MM()(
            cls.menu_modules(),
            cls.menu_admin(right=True),
            cls.menu_auth(right=True),
        )
        
        # Additional menus
        #current.menu.personal = cls.menu_personal()
        current.menu.lang = cls.menu_lang()
        current.menu.about = cls.menu_about()
        #current.menu.org = cls.menu_org()
        
        # @todo: restore?
        #current.menu.dashboard = cls.menu_dashboard()

        return main_menu

    # -------------------------------------------------------------------------
    @classmethod
    def menu_modules(cls):
        """ Custom Modules Menu """

        auth = current.auth

        if len(current.session.s3.roles) <= 2:
            # No specific Roles
            # Just show Profile on main menu
            return [MM("Profile", c="hrm", f="person",
                       args=[str(auth.s3_logged_in_person())],
                       vars={"profile":1},
                       ),
                    ]

        has_role = auth.s3_has_role
        #root_org = auth.root_org_name()
        system_roles = current.session.s3.system_roles
        ADMIN = system_roles.ADMIN
        ORG_ADMIN = system_roles.ORG_ADMIN

        s3db = current.s3db
        s3db.inv_recv_crud_strings()
        inv_recv_list = current.response.s3.crud_strings.inv_recv.title_list

        def hrm(item):
            return has_role(ORG_ADMIN) or \
                   has_role("training_coordinator") or \
                   has_role("training_assistant") or \
                   has_role("surge_manager") or \
                   has_role("disaster_manager")

        def inv(item):
            return has_role("wh_manager") or \
                   has_role("national_wh_manager") or \
                   has_role(ORG_ADMIN)

        def basic_warehouse(i):
            if not (has_role("national_wh_manager") or \
                    has_role(ORG_ADMIN)):
                # Hide menu entries which user shouldn't need access to
                return False
            else:
                return True

        def multi_warehouse(i):
            if not (has_role("national_wh_manager") or \
                    has_role(ORG_ADMIN)):
                # Only responsible for 1 warehouse so hide menu entries which should be accessed via Tabs on their warehouse.
                return False
            else:
                return True

        menu= [
                homepage("inv", "supply", "req")(                    
                   MM("Warehouses", c="inv", f="warehouse", m="summary"),
                   SEP(),
                   MM(inv_recv_list, c="inv", f="recv"),
                   MM("Sent Shipments", c="inv", f="send"),
                   SEP(),
                   MM("Items", c="supply", f="item"),
                   MM("Catalogs", c="supply", f="catalog"),
                   MM("Item Categories", c="supply", f="item_category"),
                   M("Suppliers", c="inv", f="supplier")(),
                   M("Facilities", c="inv", f="facility")(),
                   M("Requests", c="req", f="req")(),
                   #M("Commitments", f="commit")(),
               ),
               homepage("org","organisation","req")(
                    M("Organizations", f="organisation")(
                        M("Create", m="create"),
                        M("Import", m="import")
                    ),
               ),
               homepage("vol","Volunteers"),              
               homepage("project", f="project", m="summary")(
                   MM("Projects", c="project", f="project", m="summary"),
                   MM("Locations", c="project", f="location"),                  
               ),
               ]

        return menu
    
    # -------------------------------------------------------------------------
    @classmethod
    def menu_auth(cls, **attr):
        """ Auth Menu """

        auth = current.auth
        logged_in = auth.is_logged_in()

        if not logged_in:
            request = current.request
            login_next = URL(args=request.args, vars=request.vars)
            if request.controller == "default" and \
               request.function == "user" and \
               "_next" in request.get_vars:
                login_next = request.get_vars["_next"]

            self_registration = current.deployment_settings.get_security_registration_visible()
            if self_registration == "index":
                register = MM("Register", c="default", f="index", m="register",
                               vars=dict(_next=login_next),
                               check=self_registration)
            else:
                register = MM("Register", m="register",
                               vars=dict(_next=login_next),
                               check=self_registration)

            menu_auth = MM("Login", c="default", f="user", m="login",
                           _id="auth_menu_login",
                           vars=dict(_next=login_next), **attr)(
                            MM("Login", m="login",
                               vars=dict(_next=login_next)),
                            register,
                            MM("Lost Password", m="retrieve_password")
                        )
        else:
            # Logged-in
            menu_auth = MM(auth.user.email, c="default", f="user",
                           translate=False, link=False, _id="auth_menu_email",
                           **attr)(
                            MM("Logout", m="logout", _id="auth_menu_logout"),
                            MM("User Profile", m="profile"),
                            MM("Personal Data", c="default", f="person", m="update"),
                            MM("Contact Details", c="pr", f="person",
                                args="contact",
                                vars={"person.pe_id" : auth.user.pe_id}),                            
                            MM("Change Password", m="change_password"),                            
                        )

        return menu_auth
    
    # -------------------------------------------------------------------------
    @classmethod
    def menu_admin(cls, **attr):
        """ Administrator Menu """

        s3_has_role = current.auth.s3_has_role
        settings = current.deployment_settings
        name_nice = settings.modules["admin"].name_nice

        if s3_has_role("ADMIN"):
            translate = settings.has_module("translate")
            menu_admin = MM(name_nice, c="admin", **attr)(
                                MM("Settings", f="setting"),
                                MM("Users", f="user"),
                                MM("Person Registry", c="pr"),
                                MM("Database", c="appadmin", f="index"),
                                MM("Error Tickets", f="errors"),
                                MM("Synchronization", c="sync", f="index"),
                                MM("Translation", c="admin", f="translate",
                                   check=translate),
                                MM("Test Results", f="result"),
                            )
        elif s3_has_role("ORG_ADMIN"):
            menu_admin = MM(name_nice, c="admin", f="user", **attr)()
        else:
            menu_admin = None

        return menu_admin
 
 # -------------------------------------------------------------------------
    @classmethod
    def menu_org(cls):
        """ Custom Organisation Menu """

        OM = S3OrgMenuLayout
        return OM()
 # -------------------------------------------------------------------------
    @classmethod
    def menu_lang(cls):

        s3 = current.response.s3

        # Language selector
        menu_lang = ML("Language", right=True)
        for language in s3.l10n_languages.items():
            code, name = language
            menu_lang(
                ML(name, translate=False, lang_code=code, lang_name=name)
            )
        return menu_lang

    # -------------------------------------------------------------------------
    @classmethod
    def menu_about(cls):

        menu_about = MA(c="default")(
            MA("About Us", f="about"),
            MA("Contact", f="contact"),
            MA("Help", f="help"),
            MA("Privacy", f="privacy"),
        )
        return menu_about

# =============================================================================
class S3OptionsMenu(default.S3OptionsMenu):
    """ Custom Controller Menus """

    # -------------------------------------------------------------------------
    def admin(self):
        """ ADMIN menu """

        # Standard Admin Menu
        menu = super(S3OptionsMenu, self).admin()

        # Additional Items
        menu(M("Map Settings", c="gis", f="config"),
             M("Content Management", c="cms", f="index"),
             )

        return menu

    # -------------------------------------------------------------------------
    def gis(self):
        """ GIS / GIS Controllers """

        if current.request.function == "index":
            # Empty so as to leave maximum space for the Map
            # - functionality accessible via the Admin menu instead
            return None
        else:
            return super(S3OptionsMenu, self).gis()


    # -------------------------------------------------------------------------
   #def org(self):
   # #    """ Organisation Management """
   # 
   #     # Same as HRM
   #     return self.hrm()

    
    # -------------------------------------------------------------------------
    @staticmethod
    def inv():
        """ INV / Inventory """

        #auth = current.auth
        has_role = current.auth.s3_has_role
        system_roles = current.session.s3.system_roles
        ADMIN = system_roles.ADMIN
        ORG_ADMIN = system_roles.ORG_ADMIN

        s3db = current.s3db
        s3db.inv_recv_crud_strings()
        inv_recv_list = current.response.s3.crud_strings.inv_recv.title_list

        settings = current.deployment_settings
        def basic_warehouse(i):
            #if not (has_role("national_wh_manager") or \
            #        has_role(ORG_ADMIN)):
                # Hide menu entries which user shouldn't need access to
                return False
            #else:
            #    return True
        def multi_warehouse(i):
            #if not (has_role("national_wh_manager") or \
            #        has_role(ORG_ADMIN)):
                # Only responsible for 1 warehouse so hide menu entries which should be accessed via Tabs on their warehouse
                # & other things that HNRC
                return False
            #else:
            #    return True
        use_commit = lambda i: settings.get_req_use_commit()

        return M()(
                    #M("Home", f="index"),
                    M("Warehouses", c="inv", f="warehouse", m="summary", check=multi_warehouse)(
                        M("Create", m="create"),
                        M("Import", m="import", p="create"),
                    ),
                    M("Warehouse Stock", c="inv", f="inv_item", args="summary")(
                        M("Search Shipped Items", f="track_item"),
                        M("Adjust Stock Levels", f="adj"#, check=use_adjust
                          ),
                        M("Kitting", f="kitting"#, check=use_kits
                          ),
                        M("Import", f="inv_item", m="import", p="create"),
                    ),
                    M("Reports", c="inv", f="inv_item")(
                        M("Warehouse Stock", f="inv_item", m="report"),
                        M("Stock Position", f="inv_item", m="grouped",
                          vars={"report": "default"},
                          ),
                        M("Weight and Volume", f="inv_item", m="grouped",
                          vars={"report": "weight_and_volume"},
                          ),
                        M("Stock Movements", f="inv_item", m="grouped",
                          vars={"report": "movements"},
                          ),
                        M("Expiration Report", c="inv", f="track_item",
                          vars=dict(report="exp")),
                        M("Monetization Report", c="inv", f="inv_item",
                          vars=dict(report="mon")),
                        M("Utilization Report", c="inv", f="track_item",
                          vars=dict(report="util")),
                        M("Summary of Incoming Supplies", c="inv", f="track_item",
                          vars=dict(report="inc")),
                         M("Summary of Releases", c="inv", f="track_item",
                          vars=dict(report="rel")),
                    ),
                    M(inv_recv_list, c="inv", f="recv")(
                        M("Create", m="create"),
                    ),
                    M("Sent Shipments", c="inv", f="send")(
                        M("Create", m="create"),
                        M("Search Shipped Items", f="track_item"),
                    ),
                    M("Items", c="supply", f="item", m="summary", check=basic_warehouse)(
                        M("Create", m="create"),
                        M("Import", f="catalog_item", m="import", p="create", restrict=[ORG_ADMIN]),
                    ),
                    # Catalog Items moved to be next to the Item Categories
                    #M("Catalog Items", c="supply", f="catalog_item")(
                    #   M("Create", m="create"),
                    #),
                    #M("Brands", c="supply", f="brand",
                    #  restrict=[ADMIN])(
                    #    M("Create", m="create"),
                    #),
                    M("Catalogs", c="supply", f="catalog", check=basic_warehouse)(
                        M("Create", m="create"),
                    ),
                    M("Item Categories", c="supply", f="item_category",
                      restrict=[ORG_ADMIN])(
                        M("Create", m="create"),
                    ),
                    M("Suppliers", c="inv", f="supplier")(
                        M("Create", m="create"),
                        M("Import", m="import", p="create"),
                    ),
                    M("Facilities", c="inv", f="facility")(
                        M("Create", m="create", t="org_facility"),
                    ),
                    M("Facility Types", c="inv", f="facility_type",
                      restrict=[ADMIN])(
                        M("Create", m="create"),
                    ),
                    #M("Warehouse Types", c="inv", f="warehouse_type", check=use_types,
                    #  restrict=[ADMIN])(
                    #    M("Create", m="create"),
                    #),
                    M("Requests", c="req", f="req")(
                        M("Create", m="create"),
                        M("Requested Items", f="req_item"),
                    ),
                    M("Commitments", c="req", f="commit", check=use_commit)(
                    ),
                )

    # -------------------------------------------------------------------------
    def req(self):
        """ Requests Management """

        # Same as Inventory
        return self.inv()


# END =========================================================================
