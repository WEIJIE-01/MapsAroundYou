package mapsaroundyou.cli;

import mapsaroundyou.common.InvalidInputException;

import java.util.HashMap;
import java.util.Map;

/**
 * Small parser for the scaffold CLI surface.
 */
public class CliCommandParser {
    private static final java.util.Set<String> VALUE_FLAGS = java.util.Set.of(
            "--destination",
            "--max-rent",
            "--max-commute",
            "--max-transfers"
    );

    public ParsedCommand parse(String[] args) {
        if (args.length == 0) {
            return new ParsedCommand(ParsedCommand.CommandType.INTERACTIVE, null);
        }

        String firstArg = args[0];
        if (isHelp(firstArg)) {
            return new ParsedCommand(ParsedCommand.CommandType.HELP, null);
        }

        if (!"search".equals(firstArg)) {
            throw new InvalidInputException("Unknown command: " + firstArg);
        }

        if (args.length == 2 && isHelp(args[1])) {
            return new ParsedCommand(ParsedCommand.CommandType.HELP, null);
        }

        return new ParsedCommand(ParsedCommand.CommandType.SEARCH, parseSearchArguments(args));
    }

    private SearchCommandArguments parseSearchArguments(String[] args) {
        Map<String, String> options = new HashMap<>();
        boolean requireAircon = false;

        for (int index = 1; index < args.length; index++) {
            String token = args[index];
            if ("--require-aircon".equals(token)) {
                requireAircon = true;
                continue;
            }
            if (!token.startsWith("--")) {
                throw new InvalidInputException("Expected a named flag but got: " + token);
            }
            if (!VALUE_FLAGS.contains(token)) {
                throw new InvalidInputException("Unknown flag: " + token);
            }
            if (index + 1 >= args.length) {
                throw new InvalidInputException("Missing value for flag: " + token);
            }
            options.put(token, args[++index]);
        }

        String destinationId = requireOption(options, "--destination");
        int maxRent = parsePositiveOrZeroInt(requireOption(options, "--max-rent"), "--max-rent");
        int maxCommute = parsePositiveInt(requireOption(options, "--max-commute"), "--max-commute");
        int maxTransfers = parsePositiveOrZeroInt(requireOption(options, "--max-transfers"), "--max-transfers");
        return new SearchCommandArguments(destinationId, maxRent, maxCommute, maxTransfers, requireAircon);
    }

    private static String requireOption(Map<String, String> options, String optionName) {
        String value = options.get(optionName);
        if (value == null || value.isBlank()) {
            throw new InvalidInputException("Missing required flag: " + optionName);
        }
        return value.trim();
    }

    private static int parsePositiveInt(String rawValue, String optionName) {
        int value = parseInteger(rawValue, optionName);
        if (value < 1) {
            throw new InvalidInputException(optionName + " must be at least 1.");
        }
        return value;
    }

    private static int parsePositiveOrZeroInt(String rawValue, String optionName) {
        int value = parseInteger(rawValue, optionName);
        if (value < 0) {
            throw new InvalidInputException(optionName + " must be at least 0.");
        }
        return value;
    }

    private static int parseInteger(String rawValue, String optionName) {
        try {
            return Integer.parseInt(rawValue);
        } catch (NumberFormatException exception) {
            throw new InvalidInputException(optionName + " must be a valid integer.");
        }
    }

    private static boolean isHelp(String token) {
        return "-h".equals(token) || "--help".equals(token) || "help".equals(token);
    }
}
