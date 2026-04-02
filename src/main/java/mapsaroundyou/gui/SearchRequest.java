package mapsaroundyou.gui;

import mapsaroundyou.model.TransportMode;

public record SearchRequest(
        String destinationId,
        int maxRent,
        int maxCommuteMinutes,
        int maxTransfers,
        boolean requireAircon,
        TransportMode transportMode
) {
}

