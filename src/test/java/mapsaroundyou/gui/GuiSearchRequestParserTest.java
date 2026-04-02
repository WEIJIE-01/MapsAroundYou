package mapsaroundyou.gui;

import mapsaroundyou.common.InvalidInputException;
import mapsaroundyou.model.Destination;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class GuiSearchRequestParserTest {
    private static final Destination DESTINATION =
            new Destination("D01", "NUS", "University", "Kent Ridge", "117575");

    @Test
    void parse_validValues_returnsSearchRequest() {
        SearchRequest request = GuiSearchRequestParser.parse(DESTINATION, "2200", "45", "1", true);

        assertEquals("D01", request.destinationId());
        assertEquals(2200, request.maxRent());
        assertEquals(45, request.maxCommuteMinutes());
        assertEquals(1, request.maxTransfers());
        assertEquals(true, request.requireAircon());
    }

    @Test
    void parse_negativeRent_throwsInvalidInputException() {
        InvalidInputException exception = assertThrows(
                InvalidInputException.class,
            () -> GuiSearchRequestParser.parse(DESTINATION, "-1", "45", "1", false)
        );

        assertEquals("Max rent must be at least 0.", exception.getMessage());
    }

    @Test
    void parse_zeroCommute_throwsInvalidInputException() {
        InvalidInputException exception = assertThrows(
                InvalidInputException.class,
                () -> GuiSearchRequestParser.parse(DESTINATION, "2000", "0", "1", false)
        );

        assertEquals("Max commute must be at least 1.", exception.getMessage());
    }

    @Test
    void parse_negativeTransfers_throwsInvalidInputException() {
        InvalidInputException exception = assertThrows(
                InvalidInputException.class,
                () -> GuiSearchRequestParser.parse(DESTINATION, "2000", "45", "-1", false)
        );

        assertEquals("Max transfers must be at least 0.", exception.getMessage());
    }
}
