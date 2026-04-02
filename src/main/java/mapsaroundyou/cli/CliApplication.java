package mapsaroundyou.cli;

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import mapsaroundyou.common.AppConfig;
import mapsaroundyou.common.InvalidInputException;
import mapsaroundyou.common.NoResultsException;
import mapsaroundyou.logic.SearchLogic;
import mapsaroundyou.model.Destination;
import mapsaroundyou.model.TransportMode;
import mapsaroundyou.model.UserPreferences;

import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.NoSuchElementException;
import java.util.Scanner;

/**
 * Orchestrates CLI execution for interactive and flag-driven modes.
 */
public final class CliApplication {
    private final SearchLogic searchLogic;
    private final CliCommandParser commandParser;
    private final CliPrinter cliPrinter;

    @SuppressFBWarnings(
            value = "EI_EXPOSE_REP2",
            justification = "CliApplication composes shared services and does not expose mutable collaborator state."
    )
    public CliApplication(SearchLogic searchLogic, CliCommandParser commandParser, CliPrinter cliPrinter) {
        this.searchLogic = searchLogic;
        this.commandParser = commandParser;
        this.cliPrinter = cliPrinter;
    }

    public int run(String[] args) {
        cliPrinter.printBanner(searchLogic.getDatasetMetadata());

        try {
            ParsedCommand parsedCommand = commandParser.parse(args);
            return switch (parsedCommand.commandType()) {
            case HELP -> runHelp();
            case INTERACTIVE -> runInteractive();
            case SEARCH -> runSearch(parsedCommand.searchArguments());
            };
        } catch (NoResultsException exception) {
            cliPrinter.printNoResults(exception.getMessage());
            return 0;
        } catch (NoSuchElementException exception) {
            cliPrinter.printError("Interactive mode ended before all inputs were provided.");
            cliPrinter.printHelp();
            return 1;
        } catch (RuntimeException exception) {
            cliPrinter.printError(exception.getMessage());
            cliPrinter.printHelp();
            return 1;
        }
    }

    private int runHelp() {
        cliPrinter.printHelp();
        return 0;
    }

    private int runInteractive() {
        List<Destination> destinations = searchLogic.getSupportedDestinations();
        cliPrinter.printDestinations(destinations);
        cliPrinter.printInteractiveInstructions();

        try (Scanner scanner = new Scanner(System.in, StandardCharsets.UTF_8)) {
            while (true) {
                String destinationId = prompt(scanner, "Destination ID");
                if (shouldExit(destinationId)) {
                    cliPrinter.printGoodbye();
                    return 0;
                }

                try {
                    int maxRent = parseInteger(prompt(scanner, "Max rent (SGD)"), "Max rent");
                    int maxCommute = parseInteger(prompt(scanner, "Max commute (minutes)"), "Max commute");
                        int maxTransfers = parseInteger(prompt(scanner, "Max transfers"), "Max transfers");
                    boolean requireAircon = parseYesNo(prompt(scanner, "Require aircon? [y/N]"));

                    SearchCommandArguments arguments = new SearchCommandArguments(
                            destinationId,
                            maxRent,
                            maxCommute,
                            maxTransfers,
                            requireAircon
                    );
                    runSearch(arguments);
                } catch (NoResultsException exception) {
                    cliPrinter.printNoResults(exception.getMessage());
                } catch (RuntimeException exception) {
                    cliPrinter.printError(exception.getMessage());
                }

                String nextAction = prompt(scanner, "Press Enter to search again or type exit");
                if (shouldExit(nextAction)) {
                    cliPrinter.printGoodbye();
                    return 0;
                }
                System.out.println();
            }
        }
    }

    private int runSearch(SearchCommandArguments arguments) {
        searchLogic.setDestination(arguments.destinationId());
        searchLogic.setPreferences(new UserPreferences(
                arguments.destinationId(),
                arguments.maxRent(),
                arguments.maxCommuteMinutes(),
                arguments.maxTransfers(),
                arguments.requireAircon(),
                TransportMode.PUBLIC_TRANSPORT,
                AppConfig.DEFAULT_RESULT_LIMIT,
                false
        ));
        cliPrinter.printResults(searchLogic.generateShortlist());
        return 0;
    }

    private static String prompt(Scanner scanner, String label) {
        System.out.print(label + ": ");
        return scanner.nextLine().trim();
    }

    private static int parseInteger(String rawValue, String label) {
        try {
            return Integer.parseInt(rawValue);
        } catch (NumberFormatException exception) {
            throw new InvalidInputException(label + " must be a valid integer.");
        }
    }

    private static boolean parseYesNo(String rawValue) {
        if (rawValue.isBlank() || rawValue.equalsIgnoreCase("n") || rawValue.equalsIgnoreCase("no")) {
            return false;
        }
        if (rawValue.equalsIgnoreCase("y") || rawValue.equalsIgnoreCase("yes")) {
            return true;
        }
        throw new InvalidInputException("Please answer y/yes or n/no for the aircon prompt.");
    }

    private static boolean shouldExit(String rawValue) {
        return rawValue.equalsIgnoreCase("exit") || rawValue.equalsIgnoreCase("quit");
    }
}
