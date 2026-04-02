package mapsaroundyou.cli;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.time.LocalDate;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.Test;

import mapsaroundyou.common.DestinationNotFoundException;
import mapsaroundyou.logic.SearchLogic;
import mapsaroundyou.model.CommuteEstimate;
import mapsaroundyou.model.DatasetMetadata;
import mapsaroundyou.model.Destination;
import mapsaroundyou.model.ListingDetails;
import mapsaroundyou.model.SearchResult;
import mapsaroundyou.model.UserPreferences;

class CliApplicationTest {
    @Test
    void run_helpCommand_printsUsage() {
        FakeSearchLogic searchLogic = new FakeSearchLogic();
        CliApplication cliApplication = new CliApplication(searchLogic, new CliCommandParser(), new CliPrinter());

        OutputCapture outputCapture = new OutputCapture();
        int exitCode = outputCapture.run(() -> cliApplication.run(new String[]{"search", "--help"}));

        assertEquals(0, exitCode);
        assertTrue(outputCapture.stdout().contains("Usage:"));
        assertTrue(outputCapture.stdout().contains("search --destination <ID>"));
    }

    @Test
    void run_invalidDestination_returnsErrorCode() {
        SearchLogic searchLogic = new FakeSearchLogic() {
            @Override
            public void setDestination(String destinationId) {
                throw new DestinationNotFoundException("Unknown destination.");
            }
        };
        CliApplication cliApplication = new CliApplication(searchLogic, new CliCommandParser(), new CliPrinter());

        OutputCapture outputCapture = new OutputCapture();
        int exitCode = outputCapture.run(() -> cliApplication.run(
                new String[]{
                    "search", "--destination", "BAD", "--max-rent", "1800",
                    "--max-commute", "35", "--max-transfers", "1"
                }));

        assertEquals(1, exitCode);
        assertTrue(outputCapture.stderr().contains("Unknown destination."));
    }

    @Test
    void run_unknownFlag_returnsErrorCode() {
        FakeSearchLogic searchLogic = new FakeSearchLogic();
        CliApplication cliApplication = new CliApplication(searchLogic, new CliCommandParser(), new CliPrinter());

        OutputCapture outputCapture = new OutputCapture();
        int exitCode = outputCapture.run(() -> cliApplication.run(
                new String[]{
                    "search", "--destination", "D01", "--max-rentt", "1800",
                    "--max-commute", "35", "--max-transfers", "1"
                }));

        assertEquals(1, exitCode);
        assertTrue(outputCapture.stderr().contains("Unknown flag: --max-rentt"));
    }

    @Test
    void run_missingMaxTransfers_returnsErrorCode() {
        FakeSearchLogic searchLogic = new FakeSearchLogic();
        CliApplication cliApplication = new CliApplication(searchLogic, new CliCommandParser(), new CliPrinter());

        OutputCapture outputCapture = new OutputCapture();
        int exitCode = outputCapture.run(() -> cliApplication.run(
                new String[]{"search", "--destination", "D01", "--max-rent", "1800", "--max-commute", "35"}));

        assertEquals(1, exitCode);
        assertTrue(outputCapture.stderr().contains("Missing required flag: --max-transfers"));
    }

    @Test
    void run_interactiveMode_allowsSearchThenExit() {
        CountingSearchLogic searchLogic = new CountingSearchLogic();
        CliApplication cliApplication = new CliApplication(searchLogic, new CliCommandParser(), new CliPrinter());

        OutputCapture outputCapture = new OutputCapture();
        int exitCode = outputCapture.run(
                "D01\n1800\n35\n1\ny\nexit\n",
                () -> cliApplication.run(new String[]{})
        );

        assertEquals(0, exitCode);
        assertEquals(1, searchLogic.generateShortlistCalls());
        assertTrue(outputCapture.stdout().contains("Top matches:"));
        assertTrue(outputCapture.stdout().contains("Exiting MapsAroundYou CLI."));
    }

    @Test
    void run_interactiveMode_exitImmediately_returnsSuccess() {
        FakeSearchLogic searchLogic = new FakeSearchLogic();
        CliApplication cliApplication = new CliApplication(searchLogic, new CliCommandParser(), new CliPrinter());

        OutputCapture outputCapture = new OutputCapture();
        int exitCode = outputCapture.run(
                "exit\n",
                () -> cliApplication.run(new String[]{})
        );

        assertEquals(0, exitCode);
        assertTrue(outputCapture.stdout().contains("Exiting MapsAroundYou CLI."));
    }

    private static class FakeSearchLogic implements SearchLogic {
        @Override
        public List<Destination> getSupportedDestinations() {
            return List.of(new Destination("D01", "NUS", "University", "", "117575"));
        }

        @Override
        public DatasetMetadata getDatasetMetadata() {
            return new DatasetMetadata(LocalDate.of(2026, 3, 8), "Fixture dataset");
        }

        @Override
        public void setDestination(String destinationId) {
        }

        @Override
        public void setPreferences(UserPreferences preferences) {
        }

        @Override
        public List<SearchResult> generateShortlist() {
            return List.of();
        }

        @Override
        public ListingDetails getListingDetails(String listingId) {
            throw new UnsupportedOperationException();
        }

        @Override
        public CommuteEstimate getCommuteDetails(String listingId) {
            throw new UnsupportedOperationException();
        }

        @Override
        public UserPreferences getCurrentPreferences() {
            throw new UnsupportedOperationException();
        }
    }

    private static final class CountingSearchLogic extends FakeSearchLogic {
        private int generateShortlistCalls;

        @Override
        public List<SearchResult> generateShortlist() {
            generateShortlistCalls++;
            return List.of(new SearchResult(
                    new mapsaroundyou.model.RentalListing(
                            "L001",
                            "Fixture Listing",
                            1500,
                            true,
                            "R01",
                            "123 Demo Street",
                            "HDB room",
                            "Fixture",
                            "Fixture"
                    ),
                    new CommuteEstimate("R01", "D01", 30, 20, 10, 0, 1.50d),
                    0.5d
            ));
        }

        private int generateShortlistCalls() {
            return generateShortlistCalls;
        }
    }

    private static final class OutputCapture {
        private final ByteArrayOutputStream stdout = new ByteArrayOutputStream();
        private final ByteArrayOutputStream stderr = new ByteArrayOutputStream();

        private int run(IntSupplierWithException task) {
            return run("", task);
        }

        private int run(String stdin, IntSupplierWithException task) {
            PrintStream originalOut = System.out;
            PrintStream originalErr = System.err;
            java.io.InputStream originalIn = System.in;
            try (PrintStream out = new PrintStream(stdout, true, StandardCharsets.UTF_8);
                 PrintStream err = new PrintStream(stderr, true, StandardCharsets.UTF_8)) {
                System.setOut(out);
                System.setErr(err);
                System.setIn(new ByteArrayInputStream(stdin.getBytes(StandardCharsets.UTF_8)));
                return task.run();
            } catch (Exception exception) {
                throw new RuntimeException(exception);
            } finally {
                System.setOut(originalOut);
                System.setErr(originalErr);
                System.setIn(originalIn);
            }
        }

        private String stdout() {
            return stdout.toString(StandardCharsets.UTF_8);
        }

        private String stderr() {
            return stderr.toString(StandardCharsets.UTF_8);
        }
    }

    @FunctionalInterface
    private interface IntSupplierWithException {
        int run() throws Exception;
    }
}
