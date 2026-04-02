package mapsaroundyou.gui;

import java.util.List;
import java.util.Objects;

import javafx.application.Application;
import javafx.beans.property.ReadOnlyObjectWrapper;
import javafx.collections.FXCollections;
import javafx.concurrent.Task;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.CheckBox;
import javafx.scene.control.ComboBox;
import javafx.scene.control.Label;
import javafx.scene.control.ProgressIndicator;
import javafx.scene.control.SelectionMode;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableView;
import javafx.scene.control.TextField;
import javafx.scene.control.Tooltip;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.Priority;
import javafx.scene.layout.VBox;
import javafx.scene.text.Font;
import javafx.stage.Stage;
import mapsaroundyou.app.ApplicationFactory;
import mapsaroundyou.common.DataLoadException;
import mapsaroundyou.common.InvalidInputException;
import mapsaroundyou.model.DatasetMetadata;
import mapsaroundyou.model.Destination;
import mapsaroundyou.model.ListingDetails;

public final class MapsAroundYouGuiApp extends Application {
    private static final int MIN_WIDTH = 1100;
    private static final int MIN_HEIGHT = 650;

    private GuiSearchService searchService;

    private final ComboBox<Destination> destinationComboBox = new ComboBox<>();
    private final TextField maxRentField = new TextField();
    private final TextField maxCommuteField = new TextField();
    private final TextField maxTransfersField = new TextField();
    private final CheckBox requireAirconCheckBox = new CheckBox("Require aircon");
    private final Button searchButton = new Button("Search");

    private final TableView<SearchRow> resultsTable = new TableView<>();
    private final Label statusLabel = new Label("Ready.");
    private final ProgressIndicator loadingIndicator = new ProgressIndicator();
    private final Label datasetLabel = new Label();

    private final Label detailsTitle = new Label("-");
    private final Label detailsAddress = new Label("-");
    private final Label detailsRoomType = new Label("-");
    private final Label detailsRent = new Label("-");
    private final Label detailsAircon = new Label("-");
    private final Label detailsCommute = new Label("-");
    private final Label detailsScore = new Label("-");
    private final Label detailsSource = new Label("-");
    private final Label detailsNotes = new Label("-");

    @Override
    public void start(Stage stage) {
        try {
            this.searchService = new GuiSearchService(ApplicationFactory.createSearchLogic());
        } catch (DataLoadException exception) {
            showFatalStartupError(stage, exception.getMessage());
            return;
        }

        BorderPane root = new BorderPane();
        root.setPadding(new Insets(12));
        root.setTop(buildHeader());
        root.setLeft(buildControls());
        root.setCenter(buildResultsTable());
        root.setRight(buildDetailsPanel());
        root.setBottom(buildStatusBar());

        Scene scene = new Scene(root, MIN_WIDTH, MIN_HEIGHT);
        stage.setTitle("MapsAroundYou");
        stage.setMinWidth(MIN_WIDTH);
        stage.setMinHeight(MIN_HEIGHT);
        stage.setScene(scene);
        stage.show();

        configureInteractions();
        loadInitialData();
    }

    private VBox buildHeader() {
        Label title = new Label("MapsAroundYou");
        title.setFont(Font.font(20));

        datasetLabel.setWrapText(true);

        VBox header = new VBox(4, title, datasetLabel);
        header.setPadding(new Insets(0, 0, 8, 0));
        return header;
    }

    private VBox buildControls() {
        Label destinationLabel = new Label("Destination");
        destinationComboBox.setPrefWidth(280);
        destinationComboBox.setTooltip(new Tooltip("Choose a supported destination"));

        maxRentField.setPromptText("e.g. 1800");
        maxCommuteField.setPromptText("e.g. 45");
        maxTransfersField.setPromptText("e.g. 1");

        GridPane form = new GridPane();
        form.setHgap(8);
        form.setVgap(8);

        int row = 0;
        form.add(destinationLabel, 0, row);
        form.add(destinationComboBox, 1, row++);

        form.add(new Label("Max rent (SGD)"), 0, row);
        form.add(maxRentField, 1, row++);

        form.add(new Label("Max commute (minutes)"), 0, row);
        form.add(maxCommuteField, 1, row++);

        form.add(new Label("Max transfers"), 0, row);
        form.add(maxTransfersField, 1, row++);

        form.add(new Label("Aircon"), 0, row);
        form.add(requireAirconCheckBox, 1, row++);

        searchButton.setDefaultButton(true);

        VBox box = new VBox(10, form, searchButton);
        box.setPadding(new Insets(0, 12, 0, 0));
        box.setPrefWidth(360);
        return box;
    }

    private VBox buildResultsTable() {
        resultsTable.setPlaceholder(new Label("No results yet. Set filters and click Search."));
        resultsTable.getSelectionModel().setSelectionMode(SelectionMode.SINGLE);
        resultsTable.setColumnResizePolicy(TableView.CONSTRAINED_RESIZE_POLICY_ALL_COLUMNS);

        TableColumn<SearchRow, String> titleCol = new TableColumn<>("Title");
        titleCol.setCellValueFactory(cell -> new ReadOnlyObjectWrapper<>(cell.getValue().getTitle()));
        titleCol.setMinWidth(220);

        TableColumn<SearchRow, Integer> rentCol = new TableColumn<>("Rent");
        rentCol.setCellValueFactory(cell -> new ReadOnlyObjectWrapper<>(cell.getValue().getMonthlyRent()));
        rentCol.setMaxWidth(120);

        TableColumn<SearchRow, Integer> commuteCol = new TableColumn<>("Commute (min)");
        commuteCol.setCellValueFactory(cell -> new ReadOnlyObjectWrapper<>(cell.getValue().getTotalCommuteMinutes()));
        commuteCol.setMaxWidth(150);

        TableColumn<SearchRow, Boolean> airconCol = new TableColumn<>("Aircon");
        airconCol.setCellValueFactory(cell -> new ReadOnlyObjectWrapper<>(cell.getValue().hasAircon()));
        airconCol.setMaxWidth(100);

        TableColumn<SearchRow, String> scoreCol = new TableColumn<>("Score");
        scoreCol.setCellValueFactory(cell -> new ReadOnlyObjectWrapper<>(
                String.format("%.3f", cell.getValue().getScore())));
        scoreCol.setMaxWidth(120);

        resultsTable.getColumns().add(titleCol);
        resultsTable.getColumns().add(rentCol);
        resultsTable.getColumns().add(commuteCol);
        resultsTable.getColumns().add(airconCol);
        resultsTable.getColumns().add(scoreCol);

        VBox box = new VBox(resultsTable);
        VBox.setVgrow(resultsTable, Priority.ALWAYS);
        box.setPadding(new Insets(0, 12, 0, 0));
        return box;
    }

    private VBox buildDetailsPanel() {
        Label header = new Label("Details");
        header.setFont(Font.font(16));

        detailsTitle.setWrapText(true);
        detailsAddress.setWrapText(true);
        detailsNotes.setWrapText(true);

        GridPane grid = new GridPane();
        grid.setHgap(8);
        grid.setVgap(6);
        grid.setPadding(new Insets(6, 0, 0, 0));

        int row = 0;
        grid.add(new Label("Title"), 0, row);
        grid.add(detailsTitle, 1, row++);
        grid.add(new Label("Address"), 0, row);
        grid.add(detailsAddress, 1, row++);
        grid.add(new Label("Room type"), 0, row);
        grid.add(detailsRoomType, 1, row++);
        grid.add(new Label("Rent"), 0, row);
        grid.add(detailsRent, 1, row++);
        grid.add(new Label("Aircon"), 0, row);
        grid.add(detailsAircon, 1, row++);
        grid.add(new Label("Commute"), 0, row);
        grid.add(detailsCommute, 1, row++);
        grid.add(new Label("Score"), 0, row);
        grid.add(detailsScore, 1, row++);
        grid.add(new Label("Source"), 0, row);
        grid.add(detailsSource, 1, row++);
        grid.add(new Label("Notes"), 0, row);
        grid.add(detailsNotes, 1, row++);

        VBox box = new VBox(6, header, grid);
        box.setPrefWidth(320);
        return box;
    }

    private HBox buildStatusBar() {
        loadingIndicator.setVisible(false);
        loadingIndicator.setPrefSize(18, 18);

        statusLabel.setWrapText(true);
        HBox bar = new HBox(10, loadingIndicator, statusLabel);
        bar.setAlignment(Pos.CENTER_LEFT);
        bar.setPadding(new Insets(10, 0, 0, 0));
        HBox.setHgrow(statusLabel, Priority.ALWAYS);
        return bar;
    }

    private void configureInteractions() {
        destinationComboBox.setConverter(new javafx.util.StringConverter<>() {
            @Override
            public String toString(Destination destination) {
                return GuiTextFormatter.formatDestination(destination);
            }

            @Override
            public Destination fromString(String string) {
                return null;
            }
        });

        searchButton.setOnAction(event -> runSearch());

        resultsTable.getSelectionModel().selectedItemProperty().addListener((obs, oldVal, newVal) -> {
            if (newVal == null) {
                clearDetails();
                return;
            }
            populateDetails(newVal);
        });
    }

    private void loadInitialData() {
        setBusy(true, "Loading dataset...");

        Task<InitialData> initTask = new Task<>() {
            @Override
            protected InitialData call() {
                return new InitialData(
                        searchService.getSupportedDestinations(),
                        searchService.getDatasetMetadata()
                );
            }
        };

        initTask.setOnSucceeded(e -> {
            InitialData initialData = initTask.getValue();
            destinationComboBox.setItems(FXCollections.observableArrayList(initialData.destinations()));
            if (!initialData.destinations().isEmpty()) {
                destinationComboBox.getSelectionModel().select(0);
            }
            datasetLabel.setText(GuiTextFormatter.formatDatasetMetadata(initialData.metadata()));
            setBusy(false, "Ready.");
        });
        initTask.setOnFailed(e -> {
            setBusy(false, "Failed to load dataset: " + GuiErrorTranslator.toUserMessage(initTask.getException()));
        });

        GuiTaskRunner.run(initTask, "mapsaroundyou-init");
    }

    private void runSearch() {
        Destination destination = destinationComboBox.getValue();
        if (destination == null) {
            setBusy(false, "Please choose a destination.");
            return;
        }

        SearchRequest request;
        try {
            request = GuiSearchRequestParser.parse(
                    destination,
                    maxRentField.getText(),
                    maxCommuteField.getText(),
                    maxTransfersField.getText(),
                    requireAirconCheckBox.isSelected()
            );
        } catch (InvalidInputException exception) {
            setBusy(false, exception.getMessage());
            return;
        }

        setBusy(true, "Searching...");
        resultsTable.getItems().clear();
        clearDetails();

        Task<SearchResponse> task = new Task<>() {
            @Override
            protected SearchResponse call() {
                return searchService.search(request);
            }
        };

        task.setOnSucceeded(e -> {
            SearchResponse response = task.getValue();
            datasetLabel.setText(GuiTextFormatter.formatDatasetMetadata(response.datasetMetadata()));
            resultsTable.setItems(FXCollections.observableArrayList(
                    response.results().stream().map(SearchRow::new).toList()
            ));
            if (!resultsTable.getItems().isEmpty()) {
                resultsTable.getSelectionModel().select(0);
            }
            setBusy(false, "Found " + response.results().size() + " result(s).");
        });

        task.setOnFailed(e -> {
            setBusy(false, GuiErrorTranslator.toUserMessage(task.getException()));
        });

        GuiTaskRunner.run(task, "mapsaroundyou-search");
    }

    private void populateDetails(SearchRow row) {
        Objects.requireNonNull(row, "row");

        ListingDetails details;
        try {
            details = searchService.getListingDetails(row.getListingId());
        } catch (RuntimeException exception) {
            setStatus("Failed to load details: " + GuiErrorTranslator.toUserMessage(exception));
            return;
        }

        detailsTitle.setText(details.listing().title());
        detailsAddress.setText(details.listing().address());
        detailsRoomType.setText(details.listing().roomType());
        detailsRent.setText("SGD " + details.listing().monthlyRent());
        detailsAircon.setText(details.listing().hasAircon() ? "Yes" : "No");
        detailsScore.setText(String.format("%.3f", row.getScore()));
        detailsSource.setText(details.listing().sourcePlatform());
        detailsNotes.setText(GuiTextFormatter.formatOptionalText(details.listing().notes()));
        detailsCommute.setText(GuiTextFormatter.formatCommute(row.commute()));
    }

    private void clearDetails() {
        detailsTitle.setText("-");
        detailsAddress.setText("-");
        detailsRoomType.setText("-");
        detailsRent.setText("-");
        detailsAircon.setText("-");
        detailsCommute.setText("-");
        detailsScore.setText("-");
        detailsSource.setText("-");
        detailsNotes.setText("-");
    }

    private void setBusy(boolean busy, String message) {
        loadingIndicator.setVisible(busy);
        destinationComboBox.setDisable(busy);
        maxRentField.setDisable(busy);
        maxCommuteField.setDisable(busy);
        maxTransfersField.setDisable(busy);
        requireAirconCheckBox.setDisable(busy);
        searchButton.setDisable(busy);
        resultsTable.setDisable(busy);
        setStatus(message);
    }

    private void setStatus(String message) {
        statusLabel.setText(message == null || message.isBlank() ? " " : message);
    }

    private record InitialData(List<Destination> destinations, DatasetMetadata metadata) {
    }

    private static void showFatalStartupError(Stage stage, String message) {
        BorderPane root = new BorderPane();
        root.setPadding(new Insets(18));
        Label title = new Label("MapsAroundYou");
        title.setFont(Font.font(20));
        Label body = new Label("Startup error: " + (message == null ? "Unknown error" : message));
        body.setWrapText(true);
        VBox content = new VBox(10, title, body);
        root.setCenter(content);
        Scene scene = new Scene(root, 700, 200);
        stage.setTitle("MapsAroundYou");
        stage.setScene(scene);
        stage.show();
    }
}

