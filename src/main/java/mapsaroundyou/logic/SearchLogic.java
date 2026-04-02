package mapsaroundyou.logic;

import java.util.List;

import mapsaroundyou.model.CommuteEstimate;
import mapsaroundyou.model.DatasetMetadata;
import mapsaroundyou.model.Destination;
import mapsaroundyou.model.ListingDetails;
import mapsaroundyou.model.SearchResult;
import mapsaroundyou.model.UserPreferences;

public interface SearchLogic {
    List<Destination> getSupportedDestinations();

    DatasetMetadata getDatasetMetadata();

    void setDestination(String destinationId);

    void setPreferences(UserPreferences preferences);

    List<SearchResult> generateShortlist();

    ListingDetails getListingDetails(String listingId);

    CommuteEstimate getCommuteDetails(String listingId);

    UserPreferences getCurrentPreferences();
}
