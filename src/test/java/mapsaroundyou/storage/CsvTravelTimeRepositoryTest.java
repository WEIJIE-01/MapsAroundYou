package mapsaroundyou.storage;

import mapsaroundyou.common.DataLoadException;
import mapsaroundyou.model.CommuteEstimate;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class CsvTravelTimeRepositoryTest {
    @TempDir
    Path tempDir;

    @Test
    void findByOriginAndDestination_validCsv_readsTransfers() throws Exception {
        Path csvPath = tempDir.resolve("transit_matrix.csv");
        Files.writeString(csvPath, """
                flat_id,destination_id,pt_total,pt_walk,pt_transit,pt_transfers,pt_fare
                R01,D01,28,13,15,1,1.59
                """);

        CsvTravelTimeRepository repository = new CsvTravelTimeRepository(csvPath);
        Optional<CommuteEstimate> commute = repository.findByOriginAndDestination("R01", "D01");

        assertTrue(commute.isPresent());
        assertEquals(1, commute.get().transfers());
        assertEquals(28, commute.get().totalMinutes());
    }

    @Test
    void constructor_missingTransfersColumn_throwsDataLoadException() throws Exception {
        Path csvPath = tempDir.resolve("broken-transit.csv");
        Files.writeString(csvPath, """
                flat_id,destination_id,pt_total,pt_walk,pt_transit,pt_fare
                R01,D01,28,13,15,1.59
                """);

        DataLoadException exception = assertThrows(
                DataLoadException.class,
                () -> new CsvTravelTimeRepository(csvPath)
        );

        assertTrue(exception.getMessage().contains("pt_transfers"));
    }
}
