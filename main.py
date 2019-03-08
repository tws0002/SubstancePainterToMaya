##############################################
#
# SUBSTANCE PAINTER TO MAYA
#
# This tool is used to automatically connect Substance Painter textures to Arnold, VRay and Renderman for Maya.
#
# Created by Tristan Le Granche
# tristan.legranche@gmail.com
#
# Tool under licence CC-BY-NC
# Contact me for commercial use
#
# INSTALL
# Put the SubstancePainterToMaya folder in a PYTHONPATH folder (I.e: C:\Users\user\Documents\maya\scripts on Windows)
# Create a shelf button in Maya with the following Python command
# import SubstancePainterToMaya
# SubstancePainterToMaya.main.PainterToMaya()
#
# HOW TO USE
# 1. Click on the shelf button
# 2. Define the texture folder
# 3. Define the Naming Convention
# 4. Choose the renderer
# 5. Choose a materials option
# 6. Click on Launch
# 7. Specify where to plug each found maps
# 8. Choose some options
# 9. Click on Proceed
# 10. Enjoy !
#
# LIMITATIONS
# This version 0.1 only works with Arnold and uses aiStandardSurface shaders
#
# FOR MORE DETAILS
# Read the README.md file provided with the script
#
##############################################

# Libraries
import os
from PySide2 import QtCore
from PySide2 import QtWidgets
import config as cfg
import maya.cmds as mc

# Variables
PLUGIN_NAME = cfg.PLUGIN_NAME
PLUGIN_VERSION = cfg.PLUGIN_VERSION
TEXTURE_FOLDER = cfg.TEXTURE_FOLDER
PAINTER_IMAGE_EXTENSIONS = cfg.PAINTER_IMAGE_EXTENSIONS


class PainterToMaya:

    def __init__(self):

        self.baseColor = cfg.BASE_COLOR
        self.height = cfg.HEIGHT
        self.metalness = cfg.METALNESS
        self.normal = cfg.NORMAL
        self.roughness = cfg.ROUGHNESS
        self.matte = cfg.MATTE
        self.opacity = cfg.OPACITY
        self.subsurface = cfg.SUBSURFACE
        self.emission = cfg.EMISSION

        print('\n\n' + PLUGIN_NAME + ' version ' + PLUGIN_VERSION + '\n')
        self.actualWorkspace = mc.workspace(fullName=True)
        self.initUI()

    def initUI(self):
        """
        Creates the UI
        :return: None
        """

        # Create our main window
        self.mainWindow = QtWidgets.QDialog()
        self.mainWindow.setWindowTitle(PLUGIN_NAME + ' version ' + PLUGIN_VERSION)
        # self.mainWindow.setFixedSize(220,450)
        self.mainWindow.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        # Create vertical layout
        self.layVMainWindowMain = QtWidgets.QVBoxLayout()
        self.mainWindow.setLayout(self.layVMainWindowMain)
        self.mainWindow.setStyleSheet("""
                                       QGroupBox {  }
                                       """)

        # Texture Folder
        self.grpBrowseForDirectory = QtWidgets.QGroupBox('Texture Folder')
        self.layVMainWindowMain.addWidget(self.grpBrowseForDirectory)

        self.textureFolderLayout = QtWidgets.QHBoxLayout()
        self.grpBrowseForDirectory.setLayout(self.textureFolderLayout)

        # Add Texture folder widgets
        sourceImagesFolder = self.actualWorkspace + '/' + TEXTURE_FOLDER
        self.texturePath = QtWidgets.QLineEdit(sourceImagesFolder)
        self.textureFolderLayout.addWidget(self.texturePath)

        self.getButton = QtWidgets.QPushButton('Get')
        self.getButton.clicked.connect(lambda: self.getTextureFolder())
        self.textureFolderLayout.addWidget(self.getButton)

        # Naming Convention
        self.grpNamingConvention = QtWidgets.QGroupBox('Naming Convention')
        self.layVMainWindowMain.addWidget(self.grpNamingConvention)

        self.namingConventionLayout = QtWidgets.QVBoxLayout()
        self.grpNamingConvention.setLayout(self.namingConventionLayout)

        self.namingConventionSubLayout1 = QtWidgets.QVBoxLayout()
        self.namingConventionLayout.insertLayout(1, self.namingConventionSubLayout1, stretch=1)

        self.namingConventionSubLayout2 = QtWidgets.QHBoxLayout()
        self.namingConventionLayout.insertLayout(2, self.namingConventionSubLayout2, stretch=1)

        self.namingConventionSubLayout3 = QtWidgets.QVBoxLayout()
        self.namingConventionLayout.insertLayout(3, self.namingConventionSubLayout3, stretch=1)

        # Add Naming Convention widgets
        self.nomenclatureInfo = QtWidgets.QLabel(
            'Use <textureSet> and <map> into the pattern to define your convention'
        )
        self.namingConventionSubLayout1.addWidget(self.nomenclatureInfo)

        self.namingConvention = QtWidgets.QLineEdit('mesh_<textureSet>_<map>')
        self.namingConventionSubLayout2.addWidget(self.namingConvention)

        self.setNamingConventionButton = QtWidgets.QPushButton('Set')
        self.setNamingConventionButton.clicked.connect(lambda: self.setNamingConvention())
        self.namingConventionSubLayout2.addWidget(self.setNamingConventionButton)

        self.namingConventionInfo = QtWidgets.QLabel('I.e: boy_shader_baseColor.png')
        self.namingConventionLayout.addWidget(self.namingConventionInfo)

        # Renderer
        self.grpRenderer = QtWidgets.QGroupBox('Renderer')
        self.layVMainWindowMain.addWidget(self.grpRenderer)

        self.rendererLayout = QtWidgets.QVBoxLayout()
        self.grpRenderer.setLayout(self.rendererLayout)

        # Add Renderer widgets
        self.grpRadioRenderer = QtWidgets.QButtonGroup()
        self.rendererRadio1 = QtWidgets.QRadioButton('Arnold')
        self.grpRadioRenderer.addButton(self.rendererRadio1)
        self.rendererRadio1.setChecked(True)
        self.rendererRadio2 = QtWidgets.QRadioButton('VRay (to come)')
        self.rendererRadio2.setEnabled(False)
        self.grpRadioRenderer.addButton(self.rendererRadio2)
        self.rendererRadio3 = QtWidgets.QRadioButton('Renderman (to come)')
        self.rendererRadio3.setEnabled(False)
        self.grpRadioRenderer.addButton(self.rendererRadio3)

        self.rendererLayout.addWidget(self.rendererRadio1)
        self.rendererLayout.addWidget(self.rendererRadio2)
        self.rendererLayout.addWidget(self.rendererRadio3)

        # Materials
        self.grpMaterials = QtWidgets.QGroupBox('Materials')
        self.layVMainWindowMain.addWidget(self.grpMaterials)

        self.materialsLayout = QtWidgets.QVBoxLayout()
        self.grpMaterials.setLayout(self.materialsLayout)

        # Add Materials widgets
        self.grpRadioMaterials = QtWidgets.QButtonGroup()

        self.materialsRadio1 = QtWidgets.QRadioButton(
            'Use existing ones, if they don\'t exist, create new ones')
        self.grpRadioMaterials.addButton(self.materialsRadio1)
        self.materialsRadio1.setChecked(True)

        self.materialsRadio2 = QtWidgets.QRadioButton('Create new ones')
        self.grpRadioMaterials.addButton(self.materialsRadio2)

        self.materialsRadio3 = QtWidgets.QRadioButton('Use existing ones')
        self.grpRadioMaterials.addButton(self.materialsRadio3)

        self.materialsLayout.addWidget(self.materialsRadio1)
        self.materialsLayout.addWidget(self.materialsRadio2)
        self.materialsLayout.addWidget(self.materialsRadio3)

        # Launch button
        self.grpLaunch = QtWidgets.QGroupBox('Check for textures')
        self.layVMainWindowMain.addWidget(self.grpLaunch)

        self.launchLayout = QtWidgets.QVBoxLayout()
        self.grpLaunch.setLayout(self.launchLayout)

        # Add Launch widgets
        self.launchButton = QtWidgets.QPushButton('Launch')
        self.launchButton.clicked.connect(lambda: self.launch())
        self.launchLayout.addWidget(self.launchButton)

        # Found Maps
        self.grpFoundMaps = QtWidgets.QGroupBox('Found Maps')
        self.layVMainWindowMain.addWidget(self.grpFoundMaps)

        self.foundMapsLayout = QtWidgets.QVBoxLayout()
        self.grpFoundMaps.setLayout(self.foundMapsLayout)

        # Options
        self.grpOptions = QtWidgets.QGroupBox('Options')
        self.layVMainWindowMain.addWidget(self.grpOptions)

        self.optionsLayout = QtWidgets.QVBoxLayout()
        self.grpOptions.setLayout(self.optionsLayout)

        self.optionsSubLayout1 = QtWidgets.QVBoxLayout()
        self.optionsLayout.insertLayout(1, self.optionsSubLayout1, stretch=1)

        self.optionsSubLayout2 = QtWidgets.QHBoxLayout()
        self.optionsLayout.insertLayout(2, self.optionsSubLayout2, stretch=1)

        # Options Widgets
        self.checkbox1 = QtWidgets.QCheckBox('Use height as bump')
        self.optionsSubLayout1.addWidget(self.checkbox1)

        self.checkbox2 = QtWidgets.QCheckBox('Use height as displace')
        self.checkbox2.setChecked(True)
        self.optionsSubLayout1.addWidget(self.checkbox2)

        self.checkbox3 = QtWidgets.QCheckBox('Force texture replacement')
        self.checkbox3.setChecked(True)
        self.optionsSubLayout1.addWidget(self.checkbox3)

        self.checkbox4 = QtWidgets.QCheckBox('Add colorCorrect node after each file node')
        self.optionsSubLayout1.addWidget(self.checkbox4)

        self.checkbox5 = QtWidgets.QCheckBox('Add subdivisions')
        self.checkbox5.stateChanged.connect(lambda: self.addSubdivisionsCheckbox())
        self.optionsSubLayout2.addWidget(self.checkbox5)

        self.subdivTypeTitle = QtWidgets.QLabel('Type')
        self.optionsSubLayout2.addWidget(self.subdivTypeTitle)

        self.subdivType = QtWidgets.QComboBox()
        self.subdivType.addItems(['catclark', 'linear'])
        self.subdivType.setEnabled(False)
        self.optionsSubLayout2.addWidget(self.subdivType)

        self.subdivIterTitle = QtWidgets.QLabel('Iterations')
        self.optionsSubLayout2.addWidget(self.subdivIterTitle)

        self.subdivIter = QtWidgets.QLineEdit('1')
        self.subdivIter.setEnabled(False)
        self.optionsSubLayout2.addWidget(self.subdivIter)

        # Proceed
        self.grpProceed = QtWidgets.QGroupBox('Proceed')
        self.layVMainWindowMain.addWidget(self.grpProceed)

        self.proceedLayout = QtWidgets.QVBoxLayout()
        self.grpProceed.setLayout(self.proceedLayout)

        # Proceed widgets
        self.proceedButton = QtWidgets.QPushButton('Proceed')
        self.proceedButton.clicked.connect(lambda: self.main())
        self.proceedLayout.addWidget(self.proceedButton)

        # Infos
        self.grpInfos = QtWidgets.QGroupBox('Credits')
        self.layVMainWindowMain.addWidget(self.grpInfos)

        self.infosLayout = QtWidgets.QVBoxLayout()
        self.grpInfos.setLayout(self.infosLayout)

        # Infos widgets
        self.infos = QtWidgets.QLabel(cfg.INFOS)
        self.infosLayout.addWidget(self.infos)
        self.infos.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

        # Hide some
        self.grpFoundMaps.setVisible(False)
        self.grpOptions.setVisible(False)
        self.grpProceed.setVisible(False)

        global window

        try:
            window.close()
            window.deleteLater()
        except:
            pass

        window = self.mainWindow
        self.mainWindow.show()
        print('UI opened')

    def launch(self):
        """
        Check for the chosen renderer
        Load specific config file
        Display second part of interface
        Launch the texture check
        :return: None
        """

        # Check for the render engine and load config file
        if self.grpRadioRenderer.checkedId() == -2:
            import config_mtoa as config

        # Set variables
        self.mapsList = config.MAP_LIST
        self.mapsListRealAttributes = config.MAP_LIST_REAL_ATTRIBUTES
        self.mapsListColorAttributesIndices = config.MAP_LIST_COLOR_ATTRIBUTES_INDICES
        self.mapsDontUseIds = config.DONT_USE_IDS
        self.shaderToUse = config.SHADER_TO_USE
        self.normalNode = config.NORMAL_NODE
        self.bumpNode = config.BUMP_NODE

        # Display second part of the interface
        self.grpFoundMaps.setVisible(True)
        self.grpOptions.setVisible(True)
        self.grpProceed.setVisible(True)
        self.launchButton.setText('Re-launch')

        self.clearLayout(self.foundMapsLayout)

        # Populate the Found Maps part
        self.populateFoundMaps()

    def clearLayout(self, layout):
        """
        Empty specified pySide2 layout
        :param layout: Layout to clear
        :return: None
        """

        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def extractFromNomenclature(self):
        """
        Check for the naming convention specified in the interface and extract elements
        :return: position of the texture set, separator of the texture set, position of the map, separator of the map
        """

        # Load delimiters
        delimiters = cfg.DELIMITERS

        textureSetPos = mapPos = 0
        textureSetSeparator = mapPosSeparator = '_'

        # For each delimiter
        for delimiter in delimiters:

            # Split the specified naming convention
            parts = self.namingConvention.text().split(delimiter)

            # If there's a split
            if len(parts) > 1:

                # For each split
                for i in range(0, len(parts)):

                    # If the split is <textureSet>
                    if parts[i] == '<textureSet>':
                        textureSetPos = i
                        textureSetSeparator = delimiter

                    # Elif the split is <map>
                    elif parts[i] == '<map>':
                        mapPos = i
                        mapPosSeparator = delimiter

        return textureSetPos, textureSetSeparator, mapPos, mapPosSeparator

    def populateFoundMaps(self):
        """
        For all the texture files in the texture folder, create widgets in Found Maps part of the interface
        :return: None
        """

        # Initialize variables
        self.mapsFound = []
        layoutPosition = 1
        self.allTextures = []
        self.mapsFoundElements = []

        # Extract elements from naming convention
        textureSetPos, textureSetSeparator, mapPos, mapPosSeparator = self.extractFromNomenclature()

        # List texture folder elements
        textureContent = os.listdir(self.texturePath.text())

        for item in textureContent:

            # Create the texture path
            itemPath = os.path.join(self.texturePath.text(), item)

            # If item is a file
            if os.path.isfile(itemPath):

                # Get item's extension
                itemExtension = item.split('.')[1]

                # If its a valid texture file
                if itemExtension in PAINTER_IMAGE_EXTENSIONS:

                    # Add item to all textures
                    self.allTextures.append(item)

                    # Get map's name from texture's name
                    mapName = item.split(mapPosSeparator)[mapPos].split('.')[0]

                    # If the map name is not already listed (e.i: baseColor)
                    if mapName not in self.mapsFound:

                        # Get associated attribute name
                        correctMap = self.getMapFromName(mapName)

                        # Add the map to found maps
                        self.mapsFound.append(mapName)

                        # Create the layout
                        foundMapsSubLayout2 = QtWidgets.QHBoxLayout()
                        self.foundMapsLayout.insertLayout(layoutPosition, foundMapsSubLayout2, stretch=1)

                        # Create the widgets
                        map1 = QtWidgets.QLineEdit(mapName)
                        foundMapsSubLayout2.addWidget(map1)

                        map1Menu = QtWidgets.QComboBox()
                        map1Menu.addItems(self.mapsList)
                        map1Menu.setCurrentIndex(correctMap)
                        foundMapsSubLayout2.addWidget(map1Menu)

                        # Add element to map found elements
                        self.mapsFoundElements.append([map1, map1Menu])

                        # Increment layout position
                        layoutPosition += 1

    def getMapFromName(self, mapName):
        """
        Check if the map name correspond to a known attribute
        :param mapName: The name of the map
        :return: Index of the associated attribute
        """

        if mapName in self.baseColor:
            return 1
        elif mapName in self.height:
            return 2
        elif mapName in self.metalness:
            return 3
        elif mapName in self.normal:
            return 4
        elif mapName in self.roughness:
            return 5
        elif mapName in self.matte:
            return 54
        elif mapName in self.opacity:
            return 49
        elif mapName in self.subsurface:
            return 28
        elif mapName in self.emission:
            return 44
        else:
            return 0

    def getTextureFolder(self):
        """
        Get the base texture path in the interface, the file dialog start in the base texture path of the project
        :return: The texture directory
        """

        # Get project
        projectDirectory = mc.workspace(rootDirectory=True, query=True)

        # Set base texture folder
        textureFolder = projectDirectory + '/' + TEXTURE_FOLDER

        if os.path.isdir(textureFolder):
            sourceImages = textureFolder
        else:
            sourceImages = projectDirectory

        # Open a file dialog
        workDirectory = mc.fileDialog2(startingDirectory=sourceImages, fileMode=2, okCaption='Select')[0]

        # Update the texture path in the interface
        self.texturePath.setText(workDirectory)

        return workDirectory

    def setNamingConvention(self):
        """
        Change the naming convention example
        :return: The naming convention example
        """

        text = 'I.e: '

        # Change the naming convention example
        if '<textureSet>' in self.namingConvention.text() and '<map>' in self.namingConvention.text():
            text += self.namingConvention.text()

            text = text.replace('<textureSet>', 'shader')
            text = text.replace('<map>', 'baseColor')

            self.namingConventionInfo.setStyleSheet(
                'color:%s;' % 'white' +
                'font-weight:regular;'
            )

            text += '.png'

        else:
            text = 'Warning: <textureSet> and <map> are needed !'
            self.namingConventionInfo.setStyleSheet(
                'color:%s;' % 'yellow' +
                'font-weight:bold;'
            )

        self.namingConventionInfo.setText(text)

        return text

    def getMaterialFromName(self, name):
        """
        Get material's name from texture's name
        :param name: Name of the texture
        :return: The name of the material
        """

        # Extract from naming convention
        textureSetPos, textureSetSeparator, mapPos, mapPosSeparator = self.extractFromNomenclature()

        # Get the name from naming convention
        materialName = name.split(textureSetSeparator)[textureSetPos].split('.')[0]

        return materialName

    def createFileNode(self, material, mapFound, itemPath):
        """
        Creates a file node and a place2d node, set the texture of the file node and connect both of them
        :param material: The name of the material
        :param mapFound: The name of the texture map
        :param itemPath: The path of the texture map
        :return: Name of the file node
        """

        # Create a file node
        fileNode = mc.shadingNode('file', asTexture=True, isColorManaged=True, name=material + '_' + mapFound + '_file')
        # Create a place2d node
        place2d = mc.shadingNode('place2dTexture', asUtility=True, name=material + '_' + mapFound + '_place2d')

        # Add color management to the file node
        self.connectColorManagement(fileNode)

        # Set the file path of the file node
        mc.setAttr(fileNode + '.fileTextureName', itemPath, type='string')

        # Connect the file and the place2d nodes
        self.connectPlace2dTexture(place2d, fileNode)

        return fileNode

    def connectPlace2dTexture(self, place2d, fileNode):
        """
        Connect the place2d to the file node
        :param place2d: The name of the place2d node
        :param fileNode: The name of the file node
        :return: None
        """

        # Connections to make
        connections = ['rotateUV', 'offset', 'noiseUV', 'vertexCameraOne', 'vertexUvThree', 'vertexUvTwo',
                       'vertexUvOne', 'repeatUV', 'wrapV', 'wrapU', 'stagger', 'mirrorU', 'mirrorV', 'rotateFrame',
                       'translateFrame', 'coverage']

        # Basic connections
        mc.connectAttr(place2d + '.outUV', fileNode + '.uvCoord')
        mc.connectAttr(place2d + '.outUvFilterSize', fileNode + '.uvFilterSize')

        # Other connections
        for attribute in connections:
            mc.connectAttr(place2d + '.' + attribute, fileNode + '.' + attribute)

    def connectColorManagement(self, fileNode):
        """
        Add color correct management to a file node
        :param fileNode: The file node's name
        :return: None
        """

        mc.connectAttr('defaultColorMgtGlobals.cmEnabled', fileNode + '.colorManagementEnabled')
        mc.connectAttr('defaultColorMgtGlobals.configFileEnabled', fileNode + '.colorManagementConfigFileEnabled')
        mc.connectAttr('defaultColorMgtGlobals.configFilePath', fileNode + '.colorManagementConfigFilePath')
        mc.connectAttr('defaultColorMgtGlobals.workingSpaceName', fileNode + '.workingSpace')

    def connectTexture(self, textureNode, textureOutput, targetNode, targetInput):
        """
        Connect the file node to the material
        :param textureNode: Name of the file node
        :param textureOutput: Output attribute of the file node we need to use
        :param targetNode: Name of the material node
        :param targetInput: Input attribute of the material node we need to use
        :return: None
        """

        # If use colorCorrect
        if self.checkbox4.isChecked():

            # Create a colorCorrect node
            colorCorrect = mc.shadingNode('colorCorrect', asUtility=True, isColorManaged=True, )

            textureInput = textureOutput.replace('out', 'in')

            # Connect the file node to the color correct
            mc.connectAttr(textureNode + textureOutput, colorCorrect + textureInput, force=True)

            # Connect the color correct to the material
            mc.connectAttr(colorCorrect + textureOutput, targetNode + targetInput, force=True)

        # Connect the file node output to to right material input
        else:
            mc.connectAttr(textureNode + textureOutput, targetNode + targetInput, force=True)

    def addSubdivisions(self, material):
        """
        Add render subdivisions of a certain type
        :param material: The material used to find which shapes to subdivide
        :return: None
        """

        # Get values from interface
        subdivType = self.subdivType.currentIndex() + 1
        iterations = self.subdivIter.text()

        # Find the shapes connected to the material
        shader = mc.listConnections(material + '.outColor', d=True)[0]
        meshes = mc.listConnections(shader, type='mesh')

        # For all shapes add the render subdivisions
        for mesh in meshes:
            mc.setAttr(mesh + '.aiSubdivType', subdivType)
            mc.setAttr(mesh + '.aiSubdivIterations', int(iterations))

    def addSubdivisionsCheckbox(self):
        """
        Enable or disable subdivisions in the interface
        :return: None
        """

        # If subdivisions is checked
        if self.checkbox5.isChecked():
            self.subdivType.setEnabled(True)
            self.subdivIter.setEnabled(True)

        # If subdivisions is not checked
        else:
            self.subdivType.setEnabled(False)
            self.subdivIter.setEnabled(False)

    def createMaterialAndShadingGroup(self, material):
        """
        Create a material and it's shading group
        :param material: The material's name
        :return: The material's name
        """

        # Create the material
        material = mc.shadingNode(self.shaderToUse, asShader=True, name=material + '_shd')

        # Create the shading group
        shadingEngineName = material.replace('_shd', '_SG')
        shadingEngine = mc.shadingNode('shadingEngine', asPostProcess=True, name=shadingEngineName)

        # Connect the material to the shading group
        mc.connectAttr(material + '.outColor', shadingEngine + '.surfaceShader')

        return material

    def getShaderAttributeFromMapName(self, mapName):
        """
        From the map name, find the right material attribute to use
        :param mapName: The texture map's name
        :return: The name of the material attribute, the index of the material attribute
        """

        # For all the maps found elements
        for element in self.mapsFoundElements:

            # If the name of the element matches the texture's name
            if element[0].text() == mapName:

                # Get the attribute name and exist the loop
                attrName = self.mapsListRealAttributes[element[1].currentIndex()]
                break

        return attrName, element[1].currentIndex()

    def checkOrCreateMaterial(self, material):
        """
        Based on the interface options, create or use existing materials
        :param material: The material's name
        :return: The material's name, if the material was found
        """

        materialNotFound = False

        # If create new materials if they doesn't exist, instead use existing ones
        if self.grpRadioMaterials.checkedId() == -2:

            # If the material doesn't exist or if it's not of the right type
            if not mc.objExists(material) or not mc.objectType(material) == self.shaderToUse:

                # If a '_shd' version of the material doesn't exist
                if not mc.objExists(material + '_shd'):

                    # Create the material
                    material = self.createMaterialAndShadingGroup(material)

                else:

                    # Or add '_shd' at the name of the material
                    material += '_shd'

        # If create new ones
        elif self.grpRadioMaterials.checkedId() == -3:

            # If the '_shd' version of the material doesn't exist
            if not mc.objExists(material + '_shd'):

                # Create the material
                material = self.createMaterialAndShadingGroup(material)

            else:

                # Or add '_shd' at the name of the material
                material += '_shd'

        # If use existing ones
        elif self.grpRadioMaterials.checkedId() == -4:

            # If the material doesn't exist or if it's not of the right type
            if not mc.objExists(material) or not mc.objectType(material) == self.shaderToUse:

                # Specify that the material was not found
                materialNotFound = True

        return material, materialNotFound

    def createNormalMap(self, material, attributeName, forceTexture, imageNode):
        """
        Connect the normal map with the right nodes, even if a bump already exists
        :param material: The name of the material
        :param attributeName: The name of the material attribute to use
        :param forceTexture: Specify if the texture connection is forced
        :param imageNode: The file node to connect
        :return: None
        """

        # Create the normal utility
        normalNode = mc.shadingNode(self.normalNode, asUtility=True)

        # Connect the file node to the normal utility node
        self.connectTexture(imageNode, '.outColor', normalNode, '.input')

        # List the connections in the material input attribute
        connectedNodes = mc.listConnections(material + '.' + attributeName)

        # If there's connected nodes
        if connectedNodes:

            for node in connectedNodes:

                # If this is already a normal utility node
                if mc.objectType(node) == self.normalNode:

                    # Connect the new utility instead if forceTexture is true
                    mc.connectAttr(normalNode + '.outValue', material + '.' + attributeName,
                                   force=forceTexture)

                # If it's a bump node
                elif mc.objectType(node) == self.bumpNode:

                    # Get the input file of the bump node
                    connectedBumpNodes = mc.listConnections(node + '.bumpMap')
                    for connectedBumpNode in connectedBumpNodes:

                        # If it's a colorCorrect or a file node with '_file' in it's name
                        if '_file' in connectedBumpNode or 'colorCorrect' in connectedBumpNode:

                            # Connect the utility node in the bump node
                            mc.connectAttr(normalNode + '.outValue', node + '.normal',
                                           force=forceTexture)

                        else:

                            # Instead replace the bump node by the normal utility node
                            mc.connectAttr(normalNode + '.outValue', material + '.' + attributeName,
                                           force=forceTexture)

        # If there's no connections in the material attribute
        else:

            # Connect the normal utility to the material attribute
            mc.connectAttr(normalNode + '.outValue', material + '.' + attributeName,
                           force=forceTexture)

    def createBumpMap(self, material, attributeName, forceTexture, imageNode):
        """
        Connect the bump map with the right nodes, even if a normal map already exists
        :param material: The name of the material
        :param attributeName: The name of the material attribute to use
        :param forceTexture: Specify if the texture connection is forced
        :param imageNode: The file node to connect
        :return: None
        """

        # Create the bump utility node
        bumpNode = mc.shadingNode(self.bumpNode, asUtility=True)

        # Connect the file node to the bump utility node
        self.connectTexture(imageNode, '.outColorR', bumpNode, '.bumpMap')

        # List all the connection in the material attribute
        connectedNodes = mc.listConnections(material + '.' + attributeName)

        # If there's connections
        if connectedNodes:

            for node in connectedNodes:

                # If it's a normal utility node
                if mc.objectType(node) == self.normalNode:

                    # Connect the normal utility node to to bump utility
                    mc.connectAttr(node + '.outValue', material + '.normal',
                                   force=forceTexture)

                    # Connect the bump node to the material attribute
                    mc.connectAttr(bumpNode + '.outValue', material + '.' + attributeName,
                                   force=forceTexture)

                # If it's not a normal utility node
                else:

                    # Replace the connection by the bump node if the force texture is true
                    mc.connectAttr(bumpNode + '.outValue', material + '.' + attributeName,
                                   force=forceTexture)

        # If there's not connections
        else:

            # Connect the bump utility to the material attribute
            mc.connectAttr(bumpNode + '.outValue', material + '.' + attributeName,
                           force=forceTexture)

    def createDisplacementMap(self, material, forceTexture, imageNode):
        """
        Connect displacement to the right shading engine(s)
        :param material: The name of the material
        :param forceTexture: Specify if the texture connection is forced
        :param imageNode: The file node to connect
        :return: None
        """

        # Create a displacement node
        displaceNode = mc.shadingNode('displacementShader', asShader=True)

        # Connect the texture to the displacement node
        self.connectTexture(imageNode, '.outColorR', displaceNode, '.displacement')

        # Get the shading engine associated with given material
        shadingGroups = mc.listConnections(material + '.outColor')

        for shadingGroup in shadingGroups:

            # Connect the displacement node to all the found shading engines
            mc.connectAttr(displaceNode + '.displacement',
                           shadingGroup + '.displacementShader', force=forceTexture)

    def main(self):
        """
        Check if the textures need to be forced
        Creates the nodes and connect them to the right material
        :return: None
        """

        print '\nLAUNCH\n'

        # Check if the textures need to be forced
        if self.checkbox3.isChecked():
            forceTexture = True
        else:
            forceTexture = False

        # Get all textures
        for item in self.allTextures:

            # Create the texture path
            itemPath = os.path.join(self.texturePath.text(), item)
            itemPath.replace('\\', '/')

            # For all maps name found
            for mapFound in self.mapsFound:
                if mapFound in item:

                    # Get attributes from map name
                    attributeName, attributeIndex = self.getShaderAttributeFromMapName(mapFound)

                    if attributeIndex not in self.mapsDontUseIds:

                        material = self.getMaterialFromName(item)

                        # Check for material or create one
                        material, materialNotFound = self.checkOrCreateMaterial(material)

                        if materialNotFound:
                            print material + ' not found'

                        # If the material is found
                        else:
                            if mc.objExists(material):

                                # Add subdivisions
                                if self.checkbox5.isChecked():
                                    self.addSubdivisions(material)

                                # Create file node
                                imageNode = self.createFileNode(material, mapFound, itemPath)

                                # Change file node parameters to Raw and add alphaIsLuminance
                                if attributeName is not 'baseColor':
                                    try:
                                        mc.setAttr(imageNode + '.colorSpace', 'Raw', type='string')
                                    except:
                                        pass
                                    mc.setAttr(imageNode + '.alphaIsLuminance', True)

                                # Specify the output attribute to use for the file nodes
                                if attributeIndex in self.mapsListColorAttributesIndices:
                                    outputAttr = 'outColor'
                                else:
                                    outputAttr = 'outColorR'

                                # If height
                                if attributeName == 'normalCamera' and outputAttr == 'outColorR':

                                    # If bump
                                    if self.checkbox1.isChecked():

                                        self.createBumpMap(material, attributeName, forceTexture, imageNode)

                                    # If displace
                                    if self.checkbox2.isChecked():
                                        self.createDisplacementMap(material, forceTexture, imageNode)

                                # If normalMap
                                elif attributeName == 'normalCamera' and outputAttr == 'outColor':

                                    self.createNormalMap(material, attributeName, forceTexture, imageNode)

                                # If it's another type of map
                                else:
                                    self.connectTexture(imageNode, '.' + outputAttr, material, '.' + attributeName)

                    else:
                        print item + ' not used'

        print 'FINISHED'