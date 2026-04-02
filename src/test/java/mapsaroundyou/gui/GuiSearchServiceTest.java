package mapsaroundyou.gui;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import org.junit.jupiter.api.Test;

import mapsaroundyou.logic.SearchLogic;
import mapsaroundyou.model.CommuteEstimate;
import mapsaroundyou.model.DatasetMetadata;
import mapsaroundyou.model.Destination;
import mapsaroundyou.model.ListingDetails;
import mapsaroundyou.model.RentalListing;
import mapsaroundyou.model.SearchResult;
import mapsaroundyou.model.TransportMode;
import mapsaroundyou.model.UserPreferences;

class GuiSearchServiceTest {
    @Test
    void constructor_nullSearchLogic_throwsNullPointerException() {
        assertThrows(NullPointerException.class, () -> new GuiSearchService(null));
    }

    @Test
    void search_nullRequest_throwsNullPointerException() {
        GuiSearchService service = new GuiSearchService(new RecordingSearchLogic());

        assertThrows(NullPointerException.class, () -> service.search(null));
    }

    @Test
    void search_validRequest_setsSearchLogicStateAndReturnsResponse() {
        RecordingSearchLogic searchLogic = new RecordingSearchLogic();
        GuiSearchService service = new GuiSearchService(searchLogic);

        SearchRequest request = new SearchRequest("D01", 2200, 45, 1, true, TransportMode.PUBLIC_TRANSPORT);
        SearchResponse response = service.search(request);

        assertEquals("D01", searchLogic.destinationId);
        assertEquals(2200, searchLogic.maxRent);
        assertEquals(45, searchLogic.maxCommuteMinutes);
        assertEquals(1, searchLogic.maxTransfers);
        assertEquals(true, searchLogic.requireAircon);
        assertEquals(TransportMode.PUBLIC_TRANSPORT, searchLogic.transportMode);
        assertEquals(searchLogic.searchResults, response.results());
        assertEquals(searchLogic.datasetMetadata, response.datasetMetadata());
    }

    @Test
    void getSupportedDestinations_delegatesToSearchLogic() {
        RecordingSearchLogic searchLogic = new RecordingSearchLogic();
        GuiSearchService service = new GuiSearchService(searchLogic);

        List<Destination> destinations = service.getSupportedDestinations();

        assertEquals(searchLogic.supportedDestinations, destinations);
    }

    @Test
    void getDatasetMetadata_delegatesToSearchLogic() {
        RecordingSearchLogic searchLogic = new RecordingSearchLogic();
        GuiSearchService service = new GuiSearchService(searchLogic);

        DatasetMetadata metadata = service.getDatasetMetadata();

        assertEquals(searchLogic.datasetMetadata, metadata);
    }

    @Test
    void getListingDetails_delegatesToSearchLogic() {
        RecordingSearchLogic searchLogic = new RecordingSearchLogic();
        GuiSearchService service = new GuiSearchService(searchLogic);

        ListingDetails details = service.getListingDetails("L001");

        assertNotNull(details);
        assertEquals(searchLogic.listingDetails, details);
    }

    private static final class RecordingSearchLogic implements SearchLogic {
        private final List<Destination> supportedDestinations =
                List.of(new Destination("D01", "NUS", "University", "Kent Ridge", "117575"));
        private final DatasetMetadata datasetMetadata =
                new DatasetMetadata(LocalDate.of(2026, 3, 8), "Fixture dataset");
        private final SearchResult result = new SearchResult(
                new RentalListing("L001", "Listing A", 1500, true, "R01", "Addr 1", "HDB", "PG", "Note"),
                new CommuteEstimate("R01", "D01", 30, 20, 10, 0, 1.50d),
                0.42d
        );
        private final List<SearchResult> searchResults = List.of(result);
        private final ListingDetails listingDetails =
                new ListingDetails(result.listing(), Optional.of(result.commute()));

        private String destinationId;
        private int maxRent;
        private int maxCommuteMinutes;
        private int maxTransfers;
        private boolean requireAircon;
        private TransportMode transportMode;

        @Override
        public List<Destination> getSupportedDestinations() {
            return supportedDestinations;
        }

        @Override
        public DatasetMetadata getDatasetMetadata() {
            return datasetMetadata;
        }

        @Override
        public void setDestination(String destinationId) {
            this.destinationId = destinationId;
        }

        @Override
        public void setPreferences(UserPreferences preferences) {
            this.maxRent = preferences.maxRent();
            this.maxCommuteMinutes = preferences.maxCommuteMinutes();
            this.maxTransfers = preferences.maxTransfers();
            this.requireAircon = preferences.requireAircon();
            this.transportMode = preferences.transportMode();
        }

        @Override
        public List<SearchResult> generateShortlist() {
            return searchResults;
        }

        @Override
        public ListingDetails getListingDetails(String listingId) {
            return listingDetails;
        }

        @Override
        public CommuteEstimate getCommuteDetails(String listingId) {
            return result.commute();
        }

        @Override
        public UserPreferences getCurrentPreferences() {
            throw new UnsupportedOperationException();
        }
    }
}
