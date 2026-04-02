package mapsaroundyou.storage;

import java.nio.file.Path;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Optional;
import java.util.Set;

import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import mapsaroundyou.common.DataLoadException;
import mapsaroundyou.model.CommuteEstimate;

public final class CsvTravelTimeRepository implements TravelTimeRepository {
    private static final String[] REQUIRED_HEADERS = {
            "flat_id",
            "destination_id",
            "pt_total",
            "pt_walk",
            "pt_transit",
            "pt_transfers",
            "pt_fare"
    };

    private final Map<String, Map<String, CommuteEstimate>> commuteByOriginThenDestination;
    private final Set<String> knownOrigins;
    private final Set<String> knownDestinations;
    private final Map<String, Set<String>> knownDestinationsByOrigin;

    public CsvTravelTimeRepository(String resourcePath) {
        this(CsvSupport.classpathReader(resourcePath), resourcePath);
    }

    public CsvTravelTimeRepository(Path filePath) {
        this(CsvSupport.fileReader(filePath), filePath.toString());
    }

    private CsvTravelTimeRepository(ReaderSupplier readerSupplier, String sourceName) {
        this.commuteByOriginThenDestination = load(readerSupplier, sourceName);
        this.knownOrigins = Set.copyOf(commuteByOriginThenDestination.keySet());
        this.knownDestinations = commuteByOriginThenDestination.values().stream()
                .flatMap(destinationMap -> destinationMap.keySet().stream())
                .collect(java.util.stream.Collectors.toUnmodifiableSet());
        this.knownDestinationsByOrigin = buildKnownDestinationsByOrigin(commuteByOriginThenDestination);
    }

    @Override
    public Optional<CommuteEstimate> findByOriginAndDestination(String originNodeId, String destinationId) {
        return Optional.ofNullable(commuteByOriginThenDestination
                .getOrDefault(originNodeId, Map.of())
                .get(destinationId));
    }

    @Override
    public Set<String> findKnownOrigins() {
        return knownOrigins;
    }

    @Override
    @SuppressFBWarnings(
            value = "EI_EXPOSE_REP",
            justification = "knownDestinations is created once as an unmodifiable set and never mutated afterward."
    )
    public Set<String> findKnownDestinations() {
        return knownDestinations;
    }

    @Override
    @SuppressFBWarnings(
            value = "EI_EXPOSE_REP",
            justification = "knownDestinationsByOrigin is created once as an unmodifiable map of immutable sets."
    )
    public Map<String, Set<String>> findKnownDestinationsByOrigin() {
        return knownDestinationsByOrigin;
    }

    private static Map<String, Map<String, CommuteEstimate>> load(ReaderSupplier readerSupplier, String sourceName) {
        Map<String, Map<String, CommuteEstimate>> commutes = new LinkedHashMap<>();
        try (CSVParser parser = CsvSupport.openParser(readerSupplier, sourceName, REQUIRED_HEADERS)) {
            for (CSVRecord record : parser) {
                String originNodeId = CsvSupport.requireValue(record, "flat_id", sourceName);
                String destinationId = CsvSupport.requireValue(record, "destination_id", sourceName);

                Map<String, CommuteEstimate> byDestination =
                        commutes.computeIfAbsent(originNodeId, ignored -> new LinkedHashMap<>());
                if (byDestination.containsKey(destinationId)) {
                    throw new DataLoadException("Duplicate travel-time pair in " + sourceName + ": "
                            + originNodeId + " -> " + destinationId);
                }

                int ptTransfers = CsvSupport.parseRequiredInt(record, "pt_transfers", sourceName);
                if (ptTransfers < 0) {
                    throw new DataLoadException("Invalid pt_transfers value (must be non-negative) in "
                            + sourceName + " for " + originNodeId + " -> " + destinationId + ": " + ptTransfers);
                }

                CommuteEstimate commuteEstimate = new CommuteEstimate(
                        originNodeId,
                        destinationId,
                        CsvSupport.parseRequiredInt(record, "pt_total", sourceName),
                        CsvSupport.parseRequiredInt(record, "pt_transit", sourceName),
                        CsvSupport.parseRequiredInt(record, "pt_walk", sourceName),
                        ptTransfers,
                        CsvSupport.parseRequiredDouble(record, "pt_fare", sourceName)
                );
                byDestination.put(destinationId, commuteEstimate);
            }
        } catch (java.io.IOException exception) {
            throw new DataLoadException("Failed to close dataset: " + sourceName, exception);
        }
        if (commutes.isEmpty()) {
            throw new DataLoadException("No travel-time records found in " + sourceName);
        }
        return commutes;
    }

    private static Map<String, Set<String>> buildKnownDestinationsByOrigin(
            Map<String, Map<String, CommuteEstimate>> commuteByOriginThenDestination
    ) {
        Map<String, Set<String>> destinationsByOrigin = new LinkedHashMap<>();
        for (Map.Entry<String, Map<String, CommuteEstimate>> entry : commuteByOriginThenDestination.entrySet()) {
            destinationsByOrigin.put(entry.getKey(), Set.copyOf(entry.getValue().keySet()));
        }
        return Collections.unmodifiableMap(destinationsByOrigin);
    }
}
