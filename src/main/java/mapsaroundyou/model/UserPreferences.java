package mapsaroundyou.model;

/**
 * Current search preferences.
 */
public record UserPreferences(
        String destinationId,
        int maxRent,
        int maxCommuteMinutes,
        int maxTransfers,
        boolean requireAircon,
        TransportMode transportMode,
        int resultLimit,
        boolean excludeWalkDominantRoutes
) {
}
