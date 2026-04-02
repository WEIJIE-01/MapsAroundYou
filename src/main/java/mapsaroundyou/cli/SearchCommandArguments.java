package mapsaroundyou.cli;

record SearchCommandArguments(
        String destinationId,
        int maxRent,
        int maxCommuteMinutes,
        int maxTransfers,
        boolean requireAircon
) {
}
