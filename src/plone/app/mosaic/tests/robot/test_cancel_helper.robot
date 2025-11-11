*** Settings ***
Resource  keywords.robot

Test Setup  Setup Mosaic Example Page
Test Teardown  Plone test teardown

*** Test Cases ***
Cancel while adding helper should remove helper and allow further adds
    Go to  ${PLONE_URL}/example-document/edit
    Wait for Element  css=.mosaic-toolbar-primary-functions .mosaic-button-customizelayout
    Wait for then click element  css=.mosaic-toolbar-primary-functions .mosaic-button-customizelayout

    # Start inserting a richtext tile (creates helper)
    Wait for then click element  css=.select2-container.mosaic-menu-insert a
    Wait for then click element  xpath=//li[contains(@class, 'select2-option-plone\.app\.standardtiles\.html')]
    Wait until page contains element  css=.mosaic-helper-tile-new

    # Cancel the operation by simulating ESC key (should remove helper)
    Execute javascript  document.dispatchEvent(new KeyboardEvent('keydown', {keyCode:27, which:27}));
    Wait Until Element Does Not Contain  css=body  mosaic-helper-tile-new  timeout=5s

    # Now insert again and drop
    Wait for then click element  css=.select2-container.mosaic-menu-insert a
    Wait for then click element  xpath=//li[contains(@class, 'select2-option-plone\.app\.standardtiles\.html')]
    Wait until page contains element  css=.mosaic-helper-tile-new

    Click element  css=.mosaic-selected-divider
    Wait for Element  css=.mosaic-button-save
    Click button  css=.mosaic-button-save
    Run keyword and ignore error  Handle Alert  action=ACCEPT  timeout=5

    # After saving there should be no helper left
    Wait Until Element Does Not Contain  css=body  mosaic-helper-tile-new  timeout=5s

*** Keywords ***

