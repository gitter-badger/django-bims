define([
    'backbone',
    'underscore',
    'shared',
    'ol',
    'noUiSlider',
    'collections/search_result',
    'views/search_panel',
    'jquery',
    'views/filter_panel/reference_category'
], function (Backbone, _, Shared, ol, NoUiSlider, SearchResultCollection, SearchPanelView, $, ReferenceCategoryView) {

    return Backbone.View.extend({
        template: _.template($('#map-search-container').html()),
        searchBox: null,
        searchBoxOpen: false,
        searchResults: {},
        events: {
            'keyup #search': 'checkSearch',
            'keypress #search': 'searchEnter',
            'click .search-arrow': 'searchClick',
            'click .apply-filter': 'searchClick',
            'click .clear-filter': 'clearFilter',
            'click .search-reset': 'clearSearch',
        },
        initialize: function (options) {
            _.bindAll(this, 'render');
            this.parent = options.parent;
            this.sidePanel = options.sidePanel;
            this.searchPanel = new SearchPanelView();
            this.searchResultCollection = new SearchResultCollection();
            Shared.Dispatcher.on('search:searchCollection', this.search, this);
            Shared.Dispatcher.on('search:doSearch', this.searchClick, this);
            Shared.Dispatcher.on('search:clearSearch', this.clearSearch, this);
            Shared.Dispatcher.on('search:checkSearchCollection', this.checkSearch, this);
        },
        render: function () {
            this.$el.html(this.template());
            this.searchBox = this.$el.find('.map-search-box');
            this.searchInput = this.$el.find('#search');
            this.searchBox.hide();
            this.$el.append(this.searchPanel.render().$el);
            this.referenceCategoryView = new ReferenceCategoryView();
            this.$el.find('.reference-category-wrapper').append(this.referenceCategoryView.render().$el);
            return this;
        },
        checkSearch: function (forceSearch) {
            var searchValue = $('#search').val();
            if (searchValue.length > 0 && searchValue.length < 3) {
                $('#search-error-text').show();
                $('.apply-filter').attr("disabled", "disabled");
                $('.search-arrow').addClass('disabled');
            } else {
                $('#search-error-text').hide();
                $('.apply-filter').removeAttr("disabled");
                $('.search-arrow').removeClass('disabled');
            }
            if (forceSearch === true) {
                this.search(searchValue);
            }
        },
        search: function (searchValue) {
            Shared.Dispatcher.trigger('siteDetail:updateCurrentSpeciesSearchResult', []);
            if ($('#search-error-text').is(":visible")) {
                return;
            }
            var self = this;
            this.searchPanel.clearSidePanel();
            this.searchPanel.openSidePanel(false);

            $('#search-results-wrapper').html('');

            // reference category
            var referenceCategory = self.referenceCategoryView.getSelected();
            if (referenceCategory.length > 0) {
                referenceCategory = JSON.stringify(referenceCategory);
            } else {
                referenceCategory = '';
            }

            var collectorValue = [];
            $('input[name=collector-value]:checked').each(function () {
                collectorValue.push($(this).val())
            });
            if (collectorValue.length === 0) {
                collectorValue = ''
            } else {
                var encodedCollectorValue = [];
                $.each(collectorValue, function (index, value) {
                    encodedCollectorValue.push(encodeURIComponent(value));
                });
                collectorValue = encodeURIComponent(JSON.stringify(
                    collectorValue)
                );
            }

            // reference
            var referenceValue = [];
            $('input[name=reference-value]:checked').each(function () {
                referenceValue.push($(this).val())
            });
            if (referenceValue.length === 0) {
                referenceValue = ''
            } else {
                var encodedReferenceValue = [];
                $.each(referenceValue, function (index, value) {
                    encodedReferenceValue.push(encodeURIComponent(value));
                });
                referenceValue = encodeURIComponent(JSON.stringify(
                    referenceValue)
                );
            }

            var categoryValue = [];
            $('input[name=category-value]:checked').each(function () {
                categoryValue.push($(this).val())
            });
            if (categoryValue.length === 0) {
                categoryValue = ''
            } else {
                categoryValue = JSON.stringify(categoryValue)
            }

            var boundaryValue = [];
            // just get the top one.
            $('input[name=boundary-value]:checked').each(function () {
                boundaryValue.push($(this).val())
            });

            var userBoundarySelected = Shared.UserBoundarySelected;

            if (userBoundarySelected.length === 0 && boundaryValue.length === 0) {
                Shared.Dispatcher.trigger('map:boundaryEnabled', false);
                Shared.Dispatcher.trigger('map:closeHighlightPinned');
            } else {
                Shared.Dispatcher.trigger('map:boundaryEnabled', true);
            }

            if (boundaryValue.length > 0)  {
                Shared.Dispatcher.trigger('catchmentArea:show-administrative', JSON.stringify(boundaryValue));
            }

            var parameters = {
                'search': searchValue,
                'collector': collectorValue,
                'category': categoryValue,
                'boundary': boundaryValue.length === 0 ? '' : JSON.stringify(boundaryValue),
                'userBoundary': userBoundarySelected.length === 0 ? '' : JSON.stringify(userBoundarySelected),
                'yearFrom': '',
                'yearTo': '',
                'months': '',
                'reference': referenceValue,
                'referenceCategory': referenceCategory
            };
            var yearFrom = $('#year-from').html();
            var yearTo = $('#year-to').html();
            var monthSelected = [];
            if ($('#month-selector').find('input:checkbox:checked').length > 0 ||
                yearFrom != this.startYear || yearTo != this.endYear) {
                $('#month-selector').find('input:checkbox:checked').each(function () {
                    monthSelected.push($(this).val());
                });
                parameters['yearFrom'] = yearFrom;
                parameters['yearTo'] = yearTo;
                parameters['months'] = monthSelected.join(',');
            }
            Shared.Dispatcher.trigger('map:closeHighlight');
            Shared.Dispatcher.trigger('search:hit', parameters);
            Shared.Dispatcher.trigger('sidePanel:closeSidePanel');
            if (!parameters['search']
                && !parameters['collector']
                && !parameters['category']
                && !parameters['yearFrom']
                && !parameters['yearTo']
                && !parameters['userBoundary']
                && !parameters['referenceCategory']
                && !parameters['reference']
                && !parameters['boundary']) {
                Shared.Dispatcher.trigger('cluster:updateAdministrative', '');
                return false
            }
            this.searchResultCollection.search(
                this.searchPanel, parameters
            );
        },
        searchClick: function () {
            Shared.Dispatcher.trigger('map:clearAllLayers');
            var searchValue = $('#search').val();
            Shared.Router.clearSearch();
            this.search(searchValue);
        },
        searchEnter: function (e) {
            if (e.which === 13) {
                var searchValue = $('#search').val();
                Shared.Router.clearSearch();
                this.search(searchValue);
            }
        },
        clearSearch: function () {
            Shared.SearchMode = false;
            this.searchInput.val('');
            $('.clear-filter').click();
            $('.map-search-result').hide();
            this.searchPanel.clearSidePanel();

            Shared.Dispatcher.trigger('politicalRegion:clear');

            Shared.Dispatcher.trigger('spatialFilter:clearSelected');
            Shared.Dispatcher.trigger('siteDetail:updateCurrentSpeciesSearchResult', []);
            Shared.Dispatcher.trigger('cluster:updateAdministrative', '');
            Shared.Dispatcher.trigger('clusterBiological:clearClusters');

            Shared.Dispatcher.trigger('map:clearAllLayers');
            Shared.Dispatcher.trigger('map:refetchRecords');
        },
        datePickerToDate: function (element) {
            if ($(element).val()) {
                return new Date($(element).val().replace(/(\d{2})-(\d{2})-(\d{4})/, "$2/$1/$3")).getTime()
            } else {
                return '';
            }
        },
        initDateFilter: function () {
            // render slider
            this.startYear = parseInt(min_year_filter);
            this.endYear = parseInt(max_year_filter);
            this.yearSlider = NoUiSlider.create($('#year-slider')[0], {
                start: [this.startYear, this.endYear],
                connect: true,
                range: {
                    'min': this.startYear,
                    'max': this.endYear
                },
                step: 1
            });
            $('#year-from').html(this.startYear);
            $('#year-to').html(this.endYear);
            this.yearSlider.on('slide', function doSomething(values, handle, unencoded, tap, positions) {
                $('#year-from').html(Math.floor(values[0]));
                $('#year-to').html(Math.floor(values[1]));
            });

            // create month selector
            var monthSelectorHtml = '';
            var months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
            $.each(months, function (index, value) {
                if (index % 4 == 0) {
                    monthSelectorHtml += '<tr>';
                }
                monthSelectorHtml += '<td><input type="checkbox" value="' + (index + 1) + '">' + value + '</td>';
                if (index % 4 == 3) {
                    monthSelectorHtml += '</tr>';
                }
            });
            $('#month-selector').html(monthSelectorHtml);
        },
        clearFilter: function (e) {
            var target = $(e.target);
            target.closest('.row').find('input:checkbox:checked').prop('checked', false);
            if (target.closest('.row').find('#year-from').length > 0) {
                this.yearSlider.set([this.startYear, this.endYear]);
                target.closest('.row').find('#year-from').html(this.startYear);
                target.closest('.row').find('#year-to').html(this.endYear);
            }
            if (Shared.SearchMode) {
                this.searchClick();
            }
        },
        show: function () {
            this.searchBox.show();
            this.searchPanel.openSidePanel();
            this.$el.find('#search').focus();
            this.searchBoxOpen = true;
        },
        hide: function () {
            this.searchBox.hide();
            this.searchBoxOpen = false;
            this.searchPanel.hide();
        },
        isOpen: function () {
            return this.searchBoxOpen;
        }
    })

});